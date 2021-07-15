
#include <MsTimer2.h>
#define MAX_16BIT_TIMER                65535

int pin_pulseLaserAlignFibre = 8;
int pin_pulseLaserExcitation = 9;


unsigned short  overflow_;


/*
 * MsTimer2::set(unsigned long ms, void (*f)())
this function sets a time on ms for the overflow. Each overflow, "f" will be called. "f" has to be declared void with no parameters.

MsTimer2::start()
enables the interrupt.

MsTimer2::stop()
disables the interrupt.
 
 */

unsigned long cntVal;
unsigned short counterIntegrationTime_ = 100;
unsigned short nb_char;
unsigned short max_char = 8;

char buffer_entree[10];
bool isModeMonitor;


// the setup function runs once when you press reset or power the board
void setup()
{
  timer1_setup();
  Serial.begin(57600);
  pinMode(pin_pulseLaserAlignFibre, OUTPUT);
  digitalWrite(pin_pulseLaserAlignFibre, LOW);
  MsTimer2::set(counterIntegrationTime_, readCounter);
}

void timer1_setup()
{
    cli();             // disable global interrupts
    TCCR1A = 0;        // set entire TCCR1A register to 0
    TCCR1B = 0;

    // enable Timer1 overflow interrupt:
    TIMSK1 = (1 << TOIE1);
    // Set Timer 1 External clock source on T1 pin rising edge:
    TCCR1B |= (1 << CS10) | (1 << CS11) | (1 << CS12);
    // enable global interrupts:
    sei();
}

void startCounting()
{
  TCNT1 = 0; 
  overflow_ = 0;
  timer1_setup();
  MsTimer2::start();
}

void stopCounting()
{
  MsTimer2::stop();
  //cli();             // disable global interrupts
  TCNT1 = 0;
  overflow_ = 0;
  isModeMonitor = false;
}


void changeIntegrationTime()
{
  MsTimer2::set(counterIntegrationTime_, readCounter); 
}

void readCounter()
{ 
    cntVal = TCNT1 + overflow_*MAX_16BIT_TIMER;
    overflow_ = 0;
    TCNT1 = 0;
    Serial.println(cntVal);
    //Serial.print('/');
    endOfMeasurement();

}

void endOfMeasurement()
{
  if(isModeMonitor == false)
    stopCounting();
}

ISR(TIMER1_OVF_vect)
{
    //Timer 1 Overflow
    overflow_ += 1;
}


void sendCurrentValue()
{
  
  Serial.println(cntVal);
  //Serial.print('/');
}

void toggleLaserAlignFibre()
{
  digitalWrite(pin_pulseLaserAlignFibre, !digitalRead(pin_pulseLaserAlignFibre));
  //Serial.println("l");
}

void toggleLaserExcitation()
{
  digitalWrite(pin_pulseLaserExcitation, !digitalRead(pin_pulseLaserExcitation));
}

// the loop function runs over and over again until power down or reset
void loop() {

  //everything is asynchronous and dreived via Serial and timer.
}

void serialEvent() {
   if (Serial.available() > 0){
      nb_char = Serial.readBytesUntil ('/', buffer_entree, max_char);
      DecodageSerial(); 
   }
} 

void DecodageSerial () {


//Serial.println(buffer_entree);

  if(buffer_entree[0] == 'c')
  {
    // c for count
    startCounting();
  }
  else if (buffer_entree[0] == 's')
  {
    // s for stop
    stopCounting();
  }    
  else if (buffer_entree[0] == 'i')
  {
    // i for integrationTime
    counterIntegrationTime_ = (buffer_entree [1] - '0') * 10000 + (buffer_entree [2] - '0') * 1000 + (buffer_entree [3] - '0') * 100 + (buffer_entree [4] - '0') * 10 + (buffer_entree [5] - '0') * 1;    
    changeIntegrationTime();
  }   
  else if (buffer_entree[0] == 'm')
  {
    // m  for monitor
    isModeMonitor = true;
    startCounting();
  } 
  else if (buffer_entree[0] == 'l')
  {
  toggleLaserAlignFibre();   
  } 
  else if (buffer_entree[0] == 'L')
  {
  toggleLaserExcitation();   
  }   

  
  
  else if (buffer_entree[0] == '?')
  {
   Serial.println("counter/");
  } 
   
}


