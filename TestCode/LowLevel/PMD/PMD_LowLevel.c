#include "c-motion.h"
#include "PMDperiph.h"
#include "PMDsys.h"
#include "PMDdiag.h"
#include "PMDutil.h"
#include <math.h>

#include "Pro-MotionExport.c"

#define BUFSIZE   	256
#define MAX_ACC		179
#define MAX_VEL		1174405

#define FIRGELLI_POT_VOLTAGE 5

#define MAJOR_VERSION 1
#define MINOR_VERSION 0

//Point Buffers
#define BUF_INPUT  	10
#define BUF_M1      11
#define BUF_M2      12

// RAM allocation
#define RAM_CONTOUR_BASE 0
#define RAM_CONTOUR_SIZE 0x0300
#define MAXPTS (RAM_CONTOUR_SIZE/2)

#define MAX_RATE 0x01000

// Contour value buffers, these will be written to RAM on the MC58113 devices.
PMDint32 inv[MAXPTS];
PMDint32 m1v[MAXPTS];
PMDint32 m2v[MAXPTS];
PMDint32 m3v[MAXPTS];

PMDint32 M1_OFFSET = 0;
PMDint32 M2_OFFSET = 0;

PMDint32 COMMAND_INDEX = 0;
PMDuint32 WRITE_INDEX = 0;
PMDuint32 RECEIVE_INDEX = 0;
PMDuint32 STOP_INDEX = 0;
PMDint32 ACTUAL_RATE;

USER_CODE_VERSION(MAJOR_VERSION,MINOR_VERSION);

void startMotion(PMDAxisHandle* hAxis);
PMDuint32 writeBuffers(PMDAxisHandle* hAxis,int fill);
void setupUPM(PMDAxisHandle* hAxis);
PMDresult StopController(PMDAxisHandle* pAxis);
PMDresult RunController(PMDAxisHandle* pAxis,int tolerance, PMDPeriphHandle* phPeriphIO, PMDuint32 AnalogChannel);	
void ConfigureAnalogFeedbackAxis(PMDAxisHandle* pAxis);
void inverseKinematics(long delta_x, long delta_y, long* m1_steps_local, long* m2_steps_local);
void parsePacket(PMDuint8* buffer, PMDAxisHandle* hAxis, int start_index, long* a1_pos, long* a2_pos, long* a3_pos);
void linear_move(PMDAxisHandle* hAxis,PMDint32 a1_pos, PMDint32 a2_pos, PMDint32 a3_pos);
PMDint16 filterAnalog(PMDPeriphHandle* phPeriphIO, PMDuint32 AnalogChannel);

//*********************************************************************//

// Custom command declarations
typedef enum {
    PMDProfileParameterPBufferID =  0,
    PMDProfileParameterSource =     3,
    PMDProfileParameterIBufferID =  6,
    PMDProfileParameterRateScalar = 7,
    PMDProfileParameterStartIndex = 8,
    PMDProfileParameterStartValue = 9,
    PMDProfileParameterStopValue = 10
} PMDProfileParameter;

typedef enum {
    PMDTraceDataStreamValue = 90,
    PMDTraceDataStreamIndex = 91,
    PMDTraceContourOutput = 92,
    PMDTraceContourOffset = 93,
    PMDTraceActiveRateScalar = 94
} PMDXTraceVariable;

typedef enum {
    PMDUserDefinedProfile = 10
} PMDXProfileMode;

typedef enum {
    PMDBreakpointGreaterOrEqualIndex = 14,
    PMDBreakpointLessOrEqualIndex = 15
} PMDXBreakpointTrigger;

typedef enum {
    PMDErrorIBuffer = 1,
    PMDErrorOverrun = 2,
    PMDErrorPBuffer = 3,
    PMDErrorInvalidIndex = 4
} PMDRuntimeError;

typedef enum {
    PMDEventRuntimeErrorMask = 0x2000
} PMDXEventMask;

// Custom command definitions
PMDresult PMDSetProfileParameter(PMDAxisInterface axis_intf, PMDuint16 param, PMDint32 value)
{
	return SendCommandWordLong(axis_intf, 22, param, (PMDuint32)value);
}

PMDresult PMDGetProfileParameter(PMDAxisInterface axis_intf, PMDuint16 param, PMDint32 *value)
{
	return SendCommandWordGetLong(axis_intf, 23, param, (PMDuint32 *)value);
}

PMDresult PMDGetRuntimeError(PMDAxisInterface axis_intf, PMDuint16 *error)
{
	return SendCommandGetWord(axis_intf, 61, error);
}

//*********************************************************************//
//*********************************************************************//
//*********************************************************************//

USER_CODE_TASK( pmd_control )
{
	
	PMDDeviceHandle *phDevice = NULL;
	PMDPeriphHandle hPeriph;
	PMDAxisHandle hAxis[3];
	PMDPeriphHandle hPeriphIO;
	PMDuint8 data[BUFSIZE]; 
	PMDuint32 bytesReceived;
	PMDresult result = 0;
	PMDuint16 status;
	PMDint32 prev_command_index=0;
	int open = 0;
	int done = 0;
	int ready_sent = 0;
	PMDuint8 readyMessage[3] = { 0xFE, 0x00, 0xEF };

	PMD_ABORTONERROR(PMDAxisOpen(&hAxis[0], phDevice, PMDAxis1 )); 
	PMD_ABORTONERROR(PMDAxisOpen(&hAxis[1], phDevice, PMDAxis2 ));
	PMD_ABORTONERROR(PMDAxisOpen(&hAxis[2], phDevice, PMDAxis3 ));
	
	PMD_ABORTONERROR(PMDPeriphOpenPIO(&hPeriphIO, phDevice, 0, 0, PMDDataSize_16Bit));
	
	SetupAxis1(&hAxis[0]);
	SetupAxis2(&hAxis[1]);
	SetupAxis3(&hAxis[2]);
	
	ConfigureAnalogFeedbackAxis(&hAxis[2]);
	
	PMDint32 a1_pos;
	PMDint32 a2_pos;
	PMDint32 a3_pos;
	
	PMDSetPosition(&hAxis[2],(800*32768*FIRGELLI_POT_VOLTAGE)/(1000*10));
	while(!done){
		done = RunController(&hAxis[2],200,&hPeriphIO,PMDMachineIO_AICh1);
	}
	//Run Homing
	
	setupUPM(hAxis);
	
	while(1){
		PMDGetEventStatus(&hAxis[0], &status);
		PMDGetTraceValue(&hAxis[0], PMDTraceDataStreamIndex, &COMMAND_INDEX);
		PMDGetTraceValue(&hAxis[0], PMDTraceActiveRateScalar, &ACTUAL_RATE);
		
		if(prev_command_index!=COMMAND_INDEX){
			PMDSetPosition(&hAxis[2],m3v[COMMAND_INDEX]);
			PMDUpdate(&hAxis[2]);
			prev_command_index=COMMAND_INDEX;
			
			PMDprintf("rate: %d, index: %d\n",ACTUAL_RATE,COMMAND_INDEX);
		}
		done = RunController(&hAxis[2],300,&hPeriphIO,PMDMachineIO_AICh1);
		
		if(open){
			result = PMDPeriphReceive(&hPeriph, &data, &bytesReceived, BUFSIZE, 5);
			switch (result) {
				default:
				case PMD_ERR_NotConnected:
					// The peripheral handle must be closed. It will be re-opened in the outer loop.
					PMDPeriphClose(&hPeriph);
					open = 0;
					PMDprintf("Closing\n");
					startMotion(hAxis);
				break;
				case PMD_ERR_Timeout:
				break;
				case PMD_ERR_OK:
					parsePacket(data,hAxis,0,&a1_pos, &a2_pos, &a3_pos);
					ready_sent=0;
				break;
			}
			// Send Ready message if buffer can receive more data
			if(open && !ready_sent && ((RECEIVE_INDEX-COMMAND_INDEX)%MAXPTS < (MAXPTS-20))){//MAXPTS*3.0/4.0)){ 
				PMDprintf("Send Ready: ");
				result = PMDPeriphSend(&hPeriph, readyMessage, 3, 5);
				if(!result){
					ready_sent=1;
					PMDprintf(" success\n");
				}
				else{
					PMDprintf(" failed\n");
				}
			}
			
			//if(status & PMDEventBreakpoint2Mask){
			//	if(!stopped){
			//		stopped = 1;
			//		PMDSetProfileParameter(&hAxis[0], PMDProfileParameterRateScalar, 0);
			//		PMDSetProfileParameter(&hAxis[1], PMDProfileParameterRateScalar, 0);
			//		PMDMultiUpdate(&hAxis[0], 0x03);
			//	}
			//}
			//else if(stopped){
			//	PMDSetProfileParameter(&hAxis[0], PMDProfileParameterRateScalar, rate_scalar);
			//	PMDSetProfileParameter(&hAxis[1], PMDProfileParameterRateScalar, rate_scalar);
			//	PMDMultiUpdate(&hAxis[0], 0x03);
			//}
		}
		else if(done){
			result = PMDPeriphOpenTCP( &hPeriph, NULL, 0, 1234, 5000 ); // listen for a TCP connection on port 1234
			if(!result){
				PMDprintf("Connection Opened...\n");
				open = 1;
				ready_sent=0;
			}
		}
	}
}

//*********************************************************************//
//*********************************************************************//
//*********************************************************************//

void setupUPM(PMDAxisHandle* hAxis){
	int i;
	PMDuint32 npts = MAXPTS;
	
	for (i = 0; i < npts; i++) {
		inv[i] = 0;
		m1v[i] = 0;
		m2v[i] = 0;
		m3v[i] = 0;
	}
	m3v[0] = (800*32768*FIRGELLI_POT_VOLTAGE)/(1000*10);
	COMMAND_INDEX=0;
	RECEIVE_INDEX=1;
	
	// Set up synchronization
    // First set the slave side mode; its clock will stop until it gets a synch pulse.
    PMDSetSynchronizationMode( &hAxis[1], 2);

    // Now set the master side mode; both clocks should be in synch.
    PMDSetSynchronizationMode( &hAxis[0], 1);

    // Set up buffers on axis 1
    PMDSetBufferLength(&hAxis[0], BUF_INPUT, (PMDuint32) npts);
    PMDSetBufferStart(&hAxis[0], BUF_INPUT, (PMDuint32) RAM_CONTOUR_BASE);

    PMDSetBufferLength(&hAxis[0], BUF_M1, (PMDuint32) npts);
    PMDSetBufferStart(&hAxis[0], BUF_M1, (PMDuint32) RAM_CONTOUR_BASE + npts);

    for (i = 0; i < npts; i++) {
        PMDWriteBuffer(&hAxis[0], BUF_INPUT, inv[i]);
        PMDWriteBuffer(&hAxis[0], BUF_M1, m1v[i]);
    }

    // Set up buffers on axis 2
    PMDSetBufferLength(&hAxis[1], BUF_INPUT, (PMDuint32) npts);
    PMDSetBufferStart(&hAxis[1], BUF_INPUT, (PMDuint32) RAM_CONTOUR_BASE);

    PMDSetBufferLength(&hAxis[1], BUF_M2, (PMDuint32) npts);
    PMDSetBufferStart(&hAxis[1], BUF_M2, (PMDuint32) RAM_CONTOUR_BASE + npts);

    for (i = 0; i < npts; i++) {
        PMDWriteBuffer(&hAxis[1], BUF_INPUT, inv[i]);
        PMDWriteBuffer(&hAxis[1], BUF_M2, m2v[i]);
    }

    // Set up user-defined profile mode on the X axis.  This will not take effect until an update occurs.
    PMDSetProfileMode(&hAxis[0], PMDUserDefinedProfile);

    // Low byte of source is axis number,
    // high byte is the type: 0 actual position, 1 commanded position, 2 time.
    PMDSetProfileParameter(&hAxis[0], PMDProfileParameterSource, 0x200);

    PMDSetProfileParameter(&hAxis[0], PMDProfileParameterIBufferID, BUF_INPUT);
    PMDSetProfileParameter(&hAxis[0], PMDProfileParameterPBufferID, BUF_M1);

    PMDSetProfileParameter(&hAxis[0], PMDProfileParameterRateScalar, 0);

    PMDSetProfileParameter(&hAxis[0], PMDProfileParameterStartIndex, 0);
    PMDSetProfileParameter(&hAxis[0], PMDProfileParameterStartValue, 0);

    // We pick a value that does not occur in the table, so that an automatic stop
    // will not occur.
    PMDSetProfileParameter(&hAxis[0], PMDProfileParameterStopValue, -100);

    // Set up user-defined profile mode on the Y axis.
    PMDSetProfileMode(&hAxis[1], PMDUserDefinedProfile);

    // Low byte of source is axis number,
    // high byte is the type: 0 actual position, 1 commanded position, 2 time.
    PMDSetProfileParameter(&hAxis[1], PMDProfileParameterSource, 0x200);

    PMDSetProfileParameter(&hAxis[1], PMDProfileParameterIBufferID, BUF_INPUT);
    PMDSetProfileParameter(&hAxis[1], PMDProfileParameterPBufferID, BUF_M2);

    PMDSetProfileParameter(&hAxis[1], PMDProfileParameterRateScalar, 0);

    PMDSetProfileParameter(&hAxis[1], PMDProfileParameterStartIndex, 0);
    PMDSetProfileParameter(&hAxis[1], PMDProfileParameterStartValue, 0);

    // We pick a value that does not occur in the table, so that an automatic stop
    // will not occur.
    PMDSetProfileParameter(&hAxis[1], PMDProfileParameterStopValue, -100);
	
	PMDMultiUpdate(&hAxis[0], 0x03);
}

void parsePacket(PMDuint8* buffer, PMDAxisHandle* hAxis, int start_index, PMDint32* a1_pos, PMDint32* a2_pos, PMDint32* a3_pos){
	
	int i = start_index+2;
	PMDint16 x = (buffer[i+1] << 8) + buffer[i];
    PMDint16 y = (buffer[i+3] << 8) + buffer[i+2];
    PMDint16 z = (buffer[i+5] << 8) + buffer[i+4];
	
	char go_flag = (char)(buffer[i+8] & 0x01);
    char xy_abs_flag = (char)(buffer[i+8] & 0x02);
    char z_abs_flag = (char)(buffer[i+8] & 0x04);
	
	PMDint32 curr_m1 = m1v[RECEIVE_INDEX-1];
	PMDint32 curr_m2 = m2v[RECEIVE_INDEX-1];
	PMDint32 curr_z  = m3v[RECEIVE_INDEX-1];
	
	PMDint32 diff_m1;
	PMDint32 diff_m2;
	PMDint32 diff_z;
	
	inverseKinematics(x,y,a1_pos,a2_pos);
	*a3_pos = (z*32768*FIRGELLI_POT_VOLTAGE)/(1000*10);
	
	//Fix because current position is not what we are moving relative to
	if(!xy_abs_flag){
		*a1_pos += curr_m1;
		*a2_pos += curr_m2;
	}
	if(!z_abs_flag){
		PMDGetPosition(&hAxis[2],&curr_z);
		*a3_pos += curr_z;
	}
	
	//Now we have absolute postions
	
	m1v[RECEIVE_INDEX] = *a1_pos;
	m2v[RECEIVE_INDEX] = *a2_pos;
	m3v[RECEIVE_INDEX] = *a3_pos;
	
	diff_m1 = m1v[RECEIVE_INDEX] - m1v[RECEIVE_INDEX-1];
	diff_m2 = m2v[RECEIVE_INDEX] - m2v[RECEIVE_INDEX-1];
	diff_z = m3v[RECEIVE_INDEX] - m3v[RECEIVE_INDEX-1];
	
	//calculate distance traveled to use for "inv"
	inv[RECEIVE_INDEX] = inv[RECEIVE_INDEX-1]+(sqrt(diff_m1*diff_m1+diff_m2*diff_m2))/16;
	
	
	PMDprintf("diff1: %d, diff2: %d \n",diff_m1,diff_m2);
	PMDprintf("prev_inv: %d \n",inv[RECEIVE_INDEX-1]);
	PMDprintf("x: %d, y: %d, z: %d \n",x,y,z);
	PMDprintf("inv: %d \n", inv[RECEIVE_INDEX]);
	PMDprintf("m1: %d, m2: %d, m3: %d \n",*a1_pos,*a2_pos,*a3_pos);
	
	//Write to the buffer
	//writeBuffers(hAxis);
	
	RECEIVE_INDEX++;
	if(RECEIVE_INDEX==MAXPTS){
		inv[0] = inv[0];
		m1v[0] = m1v[RECEIVE_INDEX-1];
		m2v[0] = m2v[RECEIVE_INDEX-1];
		m3v[0] = m3v[RECEIVE_INDEX-1];
		
		//writeBuffers(hAxis);
		RECEIVE_INDEX = 1;
	}
	
	//PMDResetEventStatus(&hAxis[0], 0xFFFF ^ PMDEventBreakpoint2Mask);
	//PMDSetBreakpointValue(&hAxis[0], 1, RECEIVE_INDEX);
	//PMDSetBreakpoint(&hAxis[0], 1, PMDAxis1,
	//		PMDBreakpointNoAction, PMDBreakpointGreaterOrEqualIndex);
	
	if(go_flag){
		startMotion(hAxis);
	}
}

void startMotion(PMDAxisHandle* hAxis){
	PMDprintf("rate: %d, index: %d\n",ACTUAL_RATE,COMMAND_INDEX);

	PMDSetProfileParameter(&hAxis[0], PMDProfileParameterStopValue, inv[RECEIVE_INDEX-1]);
	PMDSetProfileParameter(&hAxis[1], PMDProfileParameterStopValue, inv[RECEIVE_INDEX-1]);
	
	PMDGetTraceValue(&hAxis[0], PMDTraceActiveRateScalar, &ACTUAL_RATE);
	if(ACTUAL_RATE==0){
		M1_OFFSET = m1v[COMMAND_INDEX];
		M2_OFFSET = m2v[COMMAND_INDEX];
		
		PMDprintf("Starting from stop\n");
	}
	else{
		PMDGetTraceValue(&hAxis[0], PMDTraceContourOffset, &M1_OFFSET);
		PMDGetTraceValue(&hAxis[1], PMDTraceContourOffset, &M2_OFFSET);
		PMDprintf("Continuing\n");
	}
	PMDprintf("m1_off: %d, m2_off: %d \n",M1_OFFSET,M2_OFFSET);
	
	STOP_INDEX = RECEIVE_INDEX;
	writeBuffers(hAxis,1);
	
	PMDSetProfileParameter(&hAxis[0], PMDProfileParameterRateScalar, MAX_RATE);
	PMDSetProfileParameter(&hAxis[1], PMDProfileParameterRateScalar, MAX_RATE);
	
	PMDSetPosition(&hAxis[2],m3v[COMMAND_INDEX]);
	
	PMDMultiUpdate(&hAxis[0], 0x07);
	PMDprintf("go to: %d \n",STOP_INDEX);
}
PMDuint32 writeBuffers(PMDAxisHandle* hAxis,int fill){
	PMDGetBufferWriteIndex(&hAxis[0],  BUF_INPUT,  &WRITE_INDEX);
	WRITE_INDEX=WRITE_INDEX/2;
	if(fill){
		while((STOP_INDEX-WRITE_INDEX)%MAXPTS > 0){
			PMDprintf("Writing: %d \n",WRITE_INDEX);
			PMDWriteBuffer(&hAxis[0], BUF_INPUT, inv[WRITE_INDEX]);
			PMDWriteBuffer(&hAxis[0], BUF_M1, m1v[WRITE_INDEX]-M1_OFFSET);
			PMDWriteBuffer(&hAxis[1], BUF_INPUT, inv[WRITE_INDEX]);
			PMDWriteBuffer(&hAxis[1], BUF_M2, m2v[WRITE_INDEX]-M2_OFFSET);
			
			PMDGetBufferWriteIndex(&hAxis[0],  BUF_INPUT,  &WRITE_INDEX);
			WRITE_INDEX=WRITE_INDEX/2;
		}
		return WRITE_INDEX;
	}
	else{
		PMDprintf("Writing: %d \n",WRITE_INDEX);
		PMDWriteBuffer(&hAxis[0], BUF_INPUT, inv[WRITE_INDEX]);
		PMDWriteBuffer(&hAxis[0], BUF_M1, m1v[WRITE_INDEX]);
		PMDWriteBuffer(&hAxis[1], BUF_INPUT, inv[WRITE_INDEX]);
		PMDWriteBuffer(&hAxis[1], BUF_M2, m2v[WRITE_INDEX]);
		
		PMDGetBufferWriteIndex(&hAxis[0],  BUF_INPUT,  &WRITE_INDEX);
		WRITE_INDEX=WRITE_INDEX/2;
		return WRITE_INDEX;
	}
}


void inverseKinematics(long delta_x, long delta_y, long* m1_steps_local, long* m2_steps_local){
	// 1.09 mm per 1 step. 32 microsteps per step
    float s2 = (delta_x+delta_y)*1.0*32;
    float s1 = (delta_y-delta_x)*1.0*32;

    *m1_steps_local = (long)s1;
    *m2_steps_local = (long)s2;
}


void ConfigureAnalogFeedbackAxis(PMDAxisHandle* pAxis){
	PMDprintf("Configuring Analog Feedback Axis\n");
	PMDSetMotorType(pAxis,PMDMotorTypeDCBrush);
	PMDSetOutputMode(pAxis,PMDMotorOutputAtlas);
    WaitForAtlasToConnect (pAxis);
    PMDSetOperatingMode(pAxis,0x003);  //Voltage Mode
}

PMDint16 filterAnalog(PMDPeriphHandle* phPeriphIO, PMDuint32 AnalogChannel){
	
	//Weighted Average
	static PMDint16 average = 0;
	PMDint16 actposition;
	float sigma = .75;	//Higher -> better value but slower to change
	PMDresult result;
	
	PMD_ABORTONERROR(PMDPeriphRead(phPeriphIO, &actposition, AnalogChannel, 1));
	
	average = average*(sigma)+actposition*(1-sigma);
	return average;
	
}

PMDresult RunController(PMDAxisHandle* pAxis,int tolerance, PMDPeriphHandle* phPeriphIO, PMDuint32 AnalogChannel){
    PMDint32 destination;
	PMDint16 actposition; //,command;
	int error,Kp,done,command;
	//PMDresult result;
	
	done = 0;
	Kp=40;
	PMDGetPosition(pAxis,&destination);
	
	//PMDprintf("Run To: %d\n",destination);
	
	//Read Analog position
	actposition = filterAnalog(phPeriphIO, AnalogChannel);
	//PMD_ABORTONERROR(PMDPeriphRead(phPeriphIO, &actposition, AnalogChannel, 1));
	
	//PMDprintf("Z Actual : %d \n",actposition);
	//PMDprintf("Z Desired: %d \n",destination);
	
	error=destination-actposition;
	command=error*Kp;
	//	PMDprintf("act=%d  error=%d   tol=%d\n",actposition,error,tolerance);
	if(error<0) error*=-1;
	if(error<tolerance)
	{
		PMDSetMotorCommand(pAxis,0);
		PMDUpdate(pAxis);
		done=1;
	}	
	else
    {	
		if(command>30000) command=30000;
		if(command<-30000) command=-30000;
		PMDSetMotorCommand(pAxis,command);
		PMDUpdate(pAxis);
	}
	
	// PMDprintf("mtrcmd= %d\n",command);
	return done;
}

PMDresult StopController(PMDAxisHandle* pAxis){
	PMDSetMotorCommand(pAxis,0);
	PMDUpdate(pAxis);
	return 0;
}

