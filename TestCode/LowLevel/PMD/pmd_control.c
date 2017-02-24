#include "c-motion.h"
#include "PMDperiph.h"
#include "PMDsys.h"
#include "PMDdiag.h"
#include "PMDutil.h"

#include "Pro-MotionExport.c"

#define BUFSIZE   	256
#define MAX_ACC		240
#define MAX_VEL		1174405

#define FIRGELLI_POT_VOLTAGE 5

#define MAJOR_VERSION 1
#define MINOR_VERSION 0

USER_CODE_VERSION(MAJOR_VERSION,MINOR_VERSION);

int motionComplete(PMDAxisHandle* hAxis);
PMDresult StopController(PMDAxisHandle* pAxis);
PMDresult RunController(PMDAxisHandle* pAxis,int tolerance, PMDPeriphHandle* phPeriphIO, PMDuint32 AnalogChannel);	
void ConfigureAnalogFeedbackAxis(PMDAxisHandle* pAxis);
void inverseKinematics(long delta_x, long delta_y, long* m1_steps_local, long* m2_steps_local);
void parsePacket(PMDuint8* buffer, PMDAxisHandle* hAxis, int start_index, long* a1_pos, long* a2_pos, long* a3_pos);
void linear_move(PMDAxisHandle* hAxis,PMDint32 a1_pos, PMDint32 a2_pos, PMDint32 a3_pos);
PMDint16 filterAnalog(PMDPeriphHandle* phPeriphIO, PMDuint32 AnalogChannel);

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
	PMDuint32 bytesReceived,i;
	PMDresult result = 0;
	int open = 0;
	int done = 0;
	int response_sent = 0;
	PMDuint8 readyMessage[3] = { 0xFE, 0x00, 0xEF };

	PMD_ABORTONERROR(PMDAxisOpen(&hAxis[0], phDevice, PMDAxis1 )); 
	PMD_ABORTONERROR(PMDAxisOpen(&hAxis[1], phDevice, PMDAxis2 ));
	PMD_ABORTONERROR(PMDAxisOpen(&hAxis[2], phDevice, PMDAxis3 ));
	
	PMD_ABORTONERROR(PMDPeriphOpenPIO(&hPeriphIO, phDevice, 0, 0, PMDDataSize_16Bit));
	ConfigureAnalogFeedbackAxis(&hAxis[2]);

	SetupAxis1(&hAxis[0]);
	SetupAxis2(&hAxis[1]);
	SetupAxis3(&hAxis[2]);
	
	PMDint32 a1_pos;
	PMDint32 a2_pos;
	PMDint32 a3_pos;
	
	PMDSetPosition(&hAxis[2],(800*32768*FIRGELLI_POT_VOLTAGE)/(1000*10));
	//Run Homing
	//PMDClearPositionError(phAxis[0])
	
	while(1){
		//RunController(&hAxis[2],400,&hPeriphIO,PMDMachineIO_AICh1);
		PMDprintf("Attempting to open the communications port\n");
		result = PMDPeriphOpenTCP( &hPeriph, NULL, 0, 1234, 5000 ); // listen for a TCP connection on port 1234
		if(!result){
			open = 1;
		}
		
		while(open){
			done = RunController(&hAxis[2],300,&hPeriphIO,PMDMachineIO_AICh1);
			//PMDprintf("Attempting to recieve data\n");
			result = PMDPeriphReceive(&hPeriph, &data, &bytesReceived, BUFSIZE, 5);
			//PMDprintf("result: %x \n",result);
			switch (result) {
				default:
				case PMD_ERR_NotConnected:
					// The peripheral handle must be closed. It will be re-opened in the outer loop.
					PMDPeriphClose(&hPeriph);
					open = 0;
					StopController(&hAxis[2]);
					PMDprintf("Closing\n");
					response_sent = 0;
				break;
				case PMD_ERR_Timeout:
					if(motionComplete(hAxis)&&done&&!response_sent){ //&&done
						result = PMDPeriphSend(&hPeriph, readyMessage, 3, 5);
						if(!result){
							response_sent++;
						}
					}
				break;
				case PMD_ERR_OK:
					//PMDprintf("New data received, number of bytes=%d\n", bytesReceived);
					//for(i=0; i<bytesReceived; i++)
					//{
					//	PMDprintf("Data=%x\n", data[i]);
					//}
					parsePacket(data,hAxis,0,&a1_pos, &a2_pos, &a3_pos);
					linear_move(hAxis,a1_pos,a2_pos,a3_pos);
					response_sent=0;
				break;
			}
			
			//PMDprintf("Done\n");
			//PMDPeriphClose(&hPeriph);
		}
	}
}

//*********************************************************************//
//*********************************************************************//
//*********************************************************************//

int motionComplete(PMDAxisHandle* hAxis){
	int complete = 0;
	PMDint32 actual,desired;
	
	PMDGetPosition(&hAxis[0],&desired);
	PMDGetCommandedPosition(&hAxis[0],&actual);
	complete += desired-actual;
	if(complete){
		return 0;
	}
	
	//PMDprintf("Actual: %d, Desired: %d\n",actual,desired);
	
	complete = 0;
	PMDGetPosition(&hAxis[1],&desired);
	PMDGetCommandedPosition(&hAxis[1],&actual);
	complete += desired-actual;
	if (complete){
		return 0;
	}
	
	actual = 0;
	PMDGetActualVelocity(&hAxis[0],&actual);
	if(actual){
		return 0;
	}
	
	PMDGetActualVelocity(&hAxis[1],&actual);
	if(actual){
		return 0;
	}
	//PMDprintf("Actual: %d, Desired: %d\n",actual,desired);
	
	return 1;
}

void linear_move(PMDAxisHandle* hAxis,PMDint32 a1_pos, PMDint32 a2_pos, PMDint32 a3_pos){
	PMDint32 curr_m1;
	PMDint32 curr_m2;
	
	PMDGetPosition(&hAxis[0],&curr_m1);
	PMDGetPosition(&hAxis[1],&curr_m2);
	
	PMDint32 delta_1 = a1_pos-curr_m1;
	PMDint32 delta_2 = a2_pos-curr_m2;
	
	PMDint32 vel,acc;
	
	if(delta_1<0) delta_1 *=-1;
	if(delta_2<0) delta_2 *=-1;
	
	if(delta_1>0){
		vel = (delta_1<delta_2) ? (PMDint32)(MAX_VEL*(((float)delta_1)/delta_2)) : MAX_VEL;
		acc = (delta_1<delta_2) ? (PMDint32)(MAX_ACC*(((float)delta_1)/delta_2)) : MAX_ACC;
		
		PMDprintf("M1: delta= %d, vel= %d, acc= %d \n",delta_1,vel,acc);
		
		PMDSetProfileMode(&hAxis[0], PMDTrapezoidalProfile);
		PMDSetPosition(&hAxis[0], a1_pos);
		PMDSetVelocity(&hAxis[0],  vel);
		PMDSetAcceleration(&hAxis[0], acc);
		PMDSetDeceleration(&hAxis[0], 0);
	}
	
	if(delta_2>0){
		vel = (delta_2<delta_1) ? (PMDint32)(MAX_VEL*(((float)delta_2)/delta_1)) : MAX_VEL;
		acc = (delta_2<delta_1) ? (PMDint32)(MAX_ACC*(((float)delta_2)/delta_1)) : MAX_ACC;
		
		PMDprintf("M2: delta= %d, vel= %d, acc= %d \n",delta_2,vel,acc);
		
		PMDSetProfileMode(&hAxis[1], PMDTrapezoidalProfile);
		PMDSetPosition(&hAxis[1], a2_pos);
		PMDSetVelocity(&hAxis[1], vel);
		PMDSetAcceleration(&hAxis[1], acc);
		PMDSetDeceleration(&hAxis[1], 0);
	}
	PMDSetPosition(&hAxis[2],a3_pos);
	
	PMDMultiUpdate(&hAxis[0], 0x07);
	//PMDTaskWait(10);
}

void parsePacket(PMDuint8* buffer, PMDAxisHandle* hAxis, int start_index, PMDint32* a1_pos, PMDint32* a2_pos, PMDint32* a3_pos){
	int i = start_index+2;
	PMDint16 x = (buffer[i+1] << 8) + buffer[i];
    PMDint16 y = (buffer[i+3] << 8) + buffer[i+2];
    PMDint16 z = (buffer[i+5] << 8) + buffer[i+4];
	
    char xy_abs_flag = (char)(buffer[i+8] & 0x02);
    char z_abs_flag = (char)(buffer[i+8] & 0x04);
	
	PMDint32 curr_m1;
	PMDint32 curr_m2;
	PMDint32 curr_z;

	inverseKinematics(x,y,a1_pos,a2_pos);
	*a3_pos = (z*32768*FIRGELLI_POT_VOLTAGE)/(1000*10);
	
	if(!xy_abs_flag){
		PMDGetPosition(&hAxis[0],&curr_m1);
		PMDGetPosition(&hAxis[1],&curr_m2);
		*a1_pos += curr_m1;
		*a2_pos += curr_m2;
	}
	if(!z_abs_flag){
		PMDGetPosition(&hAxis[2],&curr_z);
		*a3_pos += curr_z;
	}
	PMDprintf("\n");
	
	PMDprintf("x: %d, y: %d, z: %d \n",x,y,z);
	PMDprintf("m1: %d, m2: %d, m3: %d \n",*a1_pos,*a2_pos,*a3_pos);
}


void inverseKinematics(long delta_x, long delta_y, long* m1_steps_local, long* m2_steps_local)
{
	// 1.09 mm per 1 step. 32 microsteps per step
    float s2 = (delta_x+delta_y)*1.05*32;
    float s1 = (delta_y-delta_x)*1.05*32;

    *m1_steps_local = (long)s1;
    *m2_steps_local = (long)s2;
}


void ConfigureAnalogFeedbackAxis(PMDAxisHandle* pAxis)
{
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

PMDresult RunController(PMDAxisHandle* pAxis,int tolerance, PMDPeriphHandle* phPeriphIO, PMDuint32 AnalogChannel)
{
    PMDint32 destination;
	PMDint16 actposition; //,command;
	int error,Kp,done,command;
	PMDresult result;
	
	done = 0;
	Kp=40;
	PMDGetPosition(pAxis,&destination);
	
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


