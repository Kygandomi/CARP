//
// GenericUserPacket.c :  

// This example code runs on a CME Device connected to a host. There are two methods for sending/receiving
// user packets.  The CME user packet method transmits the user packet via a PMD Resource Protocol 
// connection.  The other method sends a raw packet over it's own interface connection, .
// The advantage to this method is that it does not include the protocol overhead of the CME method.
// This example will open a port and wait to receive any data from the host and send it back.

// TO DO: Select the interface type you are using by uncommenting the appropriate PMDPeriphOpen??? function.


#include "c-motion.h"
#include "PMDdiag.h"
#include "PMDperiph.h"
#include "PMDsys.h"

#define BUFSIZE   20 
#define MAJOR_VERSION 1
#define MINOR_VERSION 0

USER_CODE_VERSION(MAJOR_VERSION,MINOR_VERSION)

USER_CODE_TASK(pmd_ethernet)
{
	PMDPeriphHandle hPeriph;
	PMDuint8 data[BUFSIZE]; 	  
	PMDuint32 bytesReceived,i;
	PMDresult result;
	int open;
	
	memset(data, 0, BUFSIZE);

	while(1){
		PMDprintf("Attempting to open the communications port\n");
		result = PMDPeriphOpenTCP( &hPeriph, NULL, PMD_IP4_ADDR(192,168,178,1), 1234, 0 ); // listen for a TCP connection on port 1234
		open = 1;
		
		while(open){
			PMDprintf("Attempting to recieve data\n");
			result = PMDPeriphReceive(&hPeriph, &data, &bytesReceived, BUFSIZE, 5000);
			
			switch (result) {
				default:
				case PMD_ERR_NotConnected:
					// The peripheral handle must be closed. It will be re-opened in the outer loop.
					PMDPeriphClose(&hPeriph);
					open = 0;
					PMDprintf("Closing\n");
				break;
				case PMD_ERR_OK:
					PMDprintf("New data received, number of bytes=%d\n", bytesReceived);
					for(i=0; i<bytesReceived; i++)
					{
						PMDprintf("Data=%x\n", data[i]);
					}
					PMDprintf("Sending the received data\n");
					PMDPeriphSend(&hPeriph, &data, bytesReceived, 5000);
					PMDTaskWait(1000);
				break;
			}
			//PMDprintf("Done\n");
			//PMDPeriphClose(&hPeriph);
		}
	}
	PMDTaskAbort(0);
}

