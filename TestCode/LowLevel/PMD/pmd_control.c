#include "c-motion.h"
#include "PMDperiph.h"
#include "PMDsys.h"
#include "PMDdiag.h"
#include "PMDutil.h"

#include "Pro-MotionExport.c"

#define BUFSIZE   	256
#define MAX_ACC		250
#define MAX_VEL		1174405

#define HOMING_VEL 117441

#define FIRGELLI_POT_VOLTAGE 5

#define MAJOR_VERSION 1
#define MINOR_VERSION 0

#define MAXPTS (0x0300/2)

PMDint32 m1v[MAXPTS];
PMDint32 m2v[MAXPTS];
PMDint32 m3v[MAXPTS];

PMDint32 m1_vel=0;
PMDint32 m2_vel=0;

PMDint32 COMMAND_INDEX = 0;
PMDuint32 STOP_INDEX = 0;
PMDuint32 RECEIVE_INDEX = 0;

USER_CODE_VERSION(MAJOR_VERSION,MINOR_VERSION);

int motionComplete(PMDAxisHandle* hAxis);
void RunHoming(PMDAxisHandle* hAxis);
void startMotion(PMDAxisHandle* hAxis);
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
	PMDuint32 bytesReceived;
	PMDresult result = 0;
	int open = 0;
	int done = 0;
	int ready_sent = 0;
	int done_sent = 0;
	PMDuint8 readyMessage[3] = { 0xFE, 0x01, 0xEF };
	PMDuint8 doneMessage[3] = { 0xFE, 0x00, 0xEF };

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
	PMDint32 BUFF_REMAINING = MAXPTS;
	
	PMDSetPosition(&hAxis[2],(800*32768*FIRGELLI_POT_VOLTAGE)/(1000*10));
	while(!done){
		done = RunController(&hAxis[2],200,&hPeriphIO,PMDMachineIO_AICh1);
	}
	//Run Homing
	//RunHoming(hAxis);
	
	while(1){
		
		done = RunController(&hAxis[2],300,&hPeriphIO,PMDMachineIO_AICh1);
		if((COMMAND_INDEX!=STOP_INDEX) && done && motionComplete(hAxis)){
			PMDprintf("i = %d | stop = %d | recv = %d \n",COMMAND_INDEX,STOP_INDEX,RECEIVE_INDEX);
			linear_move(hAxis,m1v[COMMAND_INDEX],m2v[COMMAND_INDEX],m3v[COMMAND_INDEX]);
			COMMAND_INDEX++;
			if(COMMAND_INDEX==MAXPTS){
				COMMAND_INDEX=1;
			}
			
			BUFF_REMAINING =((PMDint32)RECEIVE_INDEX-(PMDint32)COMMAND_INDEX);
			BUFF_REMAINING = BUFF_REMAINING<0 ? -1*BUFF_REMAINING : MAXPTS-BUFF_REMAINING;
			
			done_sent = 0;
		}else if(COMMAND_INDEX==STOP_INDEX){
			m1_vel=0;
			m2_vel=0;
		}
		
		
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
					BUFF_REMAINING =((PMDint32)RECEIVE_INDEX-(PMDint32)COMMAND_INDEX);
					BUFF_REMAINING = BUFF_REMAINING<0 ? -1*BUFF_REMAINING : MAXPTS-BUFF_REMAINING;
					
					ready_sent=0;
				break;
			}
			// Send Ready message if buffer can receive more data
			if(open && !ready_sent && (BUFF_REMAINING > 20)){
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
			if(open && ready_sent && !done_sent && COMMAND_INDEX==RECEIVE_INDEX){
				PMDprintf("Send Done: ");
				result = PMDPeriphSend(&hPeriph, doneMessage, 3, 5);
				if(!result){
					done_sent=1;
					PMDprintf(" success\n");
				}
				else{
					PMDprintf(" failed\n");
				}
			}
		}
		else if(done){
			result = PMDPeriphOpenTCP( &hPeriph, NULL, 0, 1234, 500 ); // listen for a TCP connection on port 1234
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

int motionComplete(PMDAxisHandle* hAxis){
	int complete = 0;
	PMDint32 actual,desired;
	
	PMDGetPosition(&hAxis[0],&desired);
	PMDGetCommandedPosition(&hAxis[0],&actual);
	complete = desired-actual;
	if(complete){
		return 0;
	}
	
	//PMDprintf("Actual: %d, Desired: %d\n",actual,desired);
	
	complete = 0;
	PMDGetPosition(&hAxis[1],&desired);
	PMDGetCommandedPosition(&hAxis[1],&actual);
	complete = desired-actual;
	if (complete){
		return 0;
	}
	
	//actual = 0;
	//PMDGetActualVelocity(&hAxis[0],&actual);
	//if(actual){
	//	return 0;
	//}
	//
	//PMDGetActualVelocity(&hAxis[1],&actual);
	//if(actual){
	//	return 0;
	//}
	//PMDprintf("Actual: %d, Desired: %d\n",actual,desired);
	
	return 1;
}

void RunHoming(PMDAxisHandle* hAxis){
	PMDint32 error1, error2;
	int not_complete = 1;
	PMDint32 thresh = 100;
	
	// Zero Actual Positions and errors
	PMDSetActualPosition(&hAxis[0],0);
	PMDClearPositionError(&hAxis[0]);
	PMDSetActualPosition(&hAxis[1],0);
	PMDClearPositionError(&hAxis[1]);
	
	PMDMultiUpdate(&hAxis[0], 0x03);
	
	//Set Profile Mode and start Motion
	PMDResetEventStatus(&hAxis[0],0xA000);
	PMDResetEventStatus(&hAxis[0],0xEFFF);
	PMDRestoreOperatingMode(&hAxis[0]);
	PMDSetProfileMode(&hAxis[0], PMDVelocityContouringProfile);
	PMDSetVelocity(&hAxis[0], HOMING_VEL);
	PMDSetAcceleration(&hAxis[0], MAX_ACC/5);
	PMDSetDeceleration(&hAxis[0], 0);
	
	PMDResetEventStatus(&hAxis[1],0xA000);
	PMDResetEventStatus(&hAxis[1],0xEFFF);
	PMDRestoreOperatingMode(&hAxis[1]);
	PMDSetProfileMode(&hAxis[1], PMDVelocityContouringProfile);
	PMDSetVelocity(&hAxis[1],  -HOMING_VEL);
	PMDSetAcceleration(&hAxis[1], MAX_ACC/5);
	PMDSetDeceleration(&hAxis[1], 0);
	
	PMDMultiUpdate(&hAxis[0], 0x03);
	
	//Move in X until hard stop
	while(not_complete){
		PMDGetPositionError(&hAxis[0],&error1);
		PMDGetPositionError(&hAxis[1],&error2);
		
		if(error1<0) error1*=-1;
		if(error2<0) error2*=-1;
		if(error1>thresh||error2>thresh){
			PMDSetStopMode(&hAxis[0],PMDAbruptStopMode);
			PMDSetStopMode(&hAxis[1],PMDAbruptStopMode);
			PMDMultiUpdate(&hAxis[0], 0x03);
			PMDprintf("X-homing complete\n");
			not_complete=0;
		}
	}
	not_complete=1;
	
	// Zero Actual Positions and errors
	PMDSetActualPosition(&hAxis[0],0);
	PMDClearPositionError(&hAxis[0]);
	PMDSetActualPosition(&hAxis[1],0);
	PMDClearPositionError(&hAxis[1]);
	
	PMDMultiUpdate(&hAxis[0], 0x03);
	
	//Set Profile Mode and start Motion
	PMDResetEventStatus(&hAxis[0],0xA000);
	PMDResetEventStatus(&hAxis[0],0xEFFF);
	PMDRestoreOperatingMode(&hAxis[0]);
	PMDSetProfileMode(&hAxis[0], PMDVelocityContouringProfile);
	PMDSetVelocity(&hAxis[0],  -HOMING_VEL);
	PMDSetAcceleration(&hAxis[0], MAX_ACC);
	PMDSetDeceleration(&hAxis[0], 0);
	
	PMDResetEventStatus(&hAxis[1],0xA000);
	PMDResetEventStatus(&hAxis[1],0xEFFF);
	PMDRestoreOperatingMode(&hAxis[1]);
	PMDSetProfileMode(&hAxis[1], PMDVelocityContouringProfile);
	PMDSetVelocity(&hAxis[1],  -HOMING_VEL);
	PMDSetAcceleration(&hAxis[1], MAX_ACC);
	PMDSetDeceleration(&hAxis[1], 0);
	
	PMDMultiUpdate(&hAxis[0], 0x03);
	
	//Move in Y until hard stop
	while(not_complete){
		PMDGetPositionError(&hAxis[0],&error1);
		PMDGetPositionError(&hAxis[1],&error2);
		
		if(error1<0) error1*=-1;
		if(error2<0) error2*=-1;
		if((error1>thresh)||(error2>thresh)){
			PMDSetStopMode(&hAxis[0],PMDAbruptStopMode);
			PMDSetStopMode(&hAxis[1],PMDAbruptStopMode);
			PMDMultiUpdate(&hAxis[0], 0x03);
			PMDprintf("Y-homing complete\n");
			not_complete=0;
		}
	}
	not_complete=1;
	
	// Zero Actual Positions and errors
	PMDSetActualPosition(&hAxis[0],0);
	PMDClearPositionError(&hAxis[0]);
	PMDSetActualPosition(&hAxis[1],0);
	PMDClearPositionError(&hAxis[1]);
	
	PMDMultiUpdate(&hAxis[0], 0x03);
	
	PMDResetEventStatus(&hAxis[0],0xA000);
	PMDResetEventStatus(&hAxis[0],0xEFFF);
	PMDRestoreOperatingMode(&hAxis[0]);
	PMDResetEventStatus(&hAxis[1],0xA000);
	PMDResetEventStatus(&hAxis[1],0xEFFF);
	PMDRestoreOperatingMode(&hAxis[1]);
	
	PMDMultiUpdate(&hAxis[0], 0x03);
	
	PMDprintf("Homing Complete");
}
void linear_move(PMDAxisHandle* hAxis,PMDint32 a1_pos, PMDint32 a2_pos, PMDint32 a3_pos){
	PMDint32 curr_m1;
	PMDint32 curr_m2;
	
	PMDGetPosition(&hAxis[0],&curr_m1);
	PMDGetPosition(&hAxis[1],&curr_m2);
	
	PMDint32 delta_1 = a1_pos-curr_m1;
	PMDint32 delta_2 = a2_pos-curr_m2;
	
	if(delta_1<0) delta_1 *=-1;
	if(delta_2<0) delta_2 *=-1;
	
	if(delta_1>0){
		vel = (delta_1<delta_2) ? (PMDint32)(MAX_VEL*(((float)delta_1)/delta_2)) : MAX_VEL;
		acc = (delta_1<delta_2) ? (PMDint32)(MAX_ACC*(((float)delta_1)/delta_2)) : MAX_ACC;
		
		//PMDprintf("M1: delta= %d, vel= %d, acc= %d \n",delta_1,vel,acc);
		
		PMDSetProfileMode(&hAxis[0], PMDTrapezoidalProfile);
		PMDSetPosition(&hAxis[0], a1_pos);
		PMDSetVelocity(&hAxis[0],  vel);
		//PMDSetStartVelocity(&hAxis[0],m1_vel);
		PMDSetAcceleration(&hAxis[0], acc);
		PMDSetDeceleration(&hAxis[0], 0);
		
		m1_vel = vel;
	}else{
		m1_vel = 0;
	}
	
	if(delta_2>0){
		vel = (delta_2<delta_1) ? (PMDint32)(MAX_VEL*(((float)delta_2)/delta_1)) : MAX_VEL;
		acc = (delta_2<delta_1) ? (PMDint32)(MAX_ACC*(((float)delta_2)/delta_1)) : MAX_ACC;
		
		//PMDprintf("M2: delta= %d, vel= %d, acc= %d \n",delta_2,vel,acc);
		
		PMDSetProfileMode(&hAxis[1], PMDTrapezoidalProfile);
		PMDSetPosition(&hAxis[1], a2_pos);
		//PMDSetStartVelocity(&hAxis[1],m2_vel);
		PMDSetVelocity(&hAxis[1], vel);
		PMDSetAcceleration(&hAxis[1], acc);
		PMDSetDeceleration(&hAxis[1], 0);
		
		m2_vel = vel;
	}else{
		m2_vel = 0;
	}
	
	PMDSetPosition(&hAxis[2],a3_pos);
	
	PMDMultiUpdate(&hAxis[0], 0x07);
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
		*a3_pos += curr_z;
	}
	
	//Now we have absolute postions
	
	m1v[RECEIVE_INDEX] = *a1_pos;
	m2v[RECEIVE_INDEX] = *a2_pos;
	m3v[RECEIVE_INDEX] = *a3_pos;
	
	diff_m1 = m1v[RECEIVE_INDEX] - m1v[RECEIVE_INDEX-1];
	diff_m2 = m2v[RECEIVE_INDEX] - m2v[RECEIVE_INDEX-1];
	diff_z = m3v[RECEIVE_INDEX] - m3v[RECEIVE_INDEX-1];

	
	//PMDprintf("x: %d, y: %d, z: %d \n",x,y,z);
	//PMDprintf("m1: %d, m2: %d, m3: %d \n",*a1_pos,*a2_pos,*a3_pos);
	//PMDprintf("diff1: %d, diff2: %d ,diff3: %d\n",diff_m1,diff_m2,diff_z);
	
	RECEIVE_INDEX++;
	if(RECEIVE_INDEX==MAXPTS){
		m1v[0] = m1v[RECEIVE_INDEX-1];
		m2v[0] = m2v[RECEIVE_INDEX-1];
		m3v[0] = m3v[RECEIVE_INDEX-1];
		
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
	
	STOP_INDEX = RECEIVE_INDEX;
	//linear_move(hAxis,m1v[COMMAND_INDEX],m2v[COMMAND_INDEX],m3v[COMMAND_INDEX]);
	
	PMDprintf("go to: %d \n",STOP_INDEX);
}
void inverseKinematics(long delta_x, long delta_y, long* m1_steps_local, long* m2_steps_local)
{
	// 1.09 mm per 1 step. 32 microsteps per step
    float s2 = (delta_x+delta_y)*1.0*32;
    float s1 = (delta_y-delta_x)*1.0*32;

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
	float sigma = .70;	//Higher -> better value but slower to change
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
		done=0;
	}	
	else
    {	
		if(command>30000) command=30000;
		if(command<-30000) command=-30000;
		PMDSetMotorCommand(pAxis,command);
		PMDUpdate(pAxis);
	}
	
	// PMDprintf("mtrcmd= %d\n",command);
	return 0;
}

PMDresult StopController(PMDAxisHandle* pAxis){
	PMDSetMotorCommand(pAxis,0);
	PMDUpdate(pAxis);
	return 0;
}


