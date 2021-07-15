#!/usr/bin/env python
#-*- coding: utf-8 -*-



from XYStage import XYStage

import ctypes
import atexit

class ErrorCodes:
    # Task has been completed successfully.
    MCL_SUCCESS = 0

    # These errors generally occur due to an internal sanity check failing.
    MCL_GENERAL_ERROR = -1

    # A problem occurred when transferring data to the Micro-Drive.
    # It is likely that the Micro-Drive will have to be 	 power cycled to correct these errors.
    MCL_DEV_ERROR = -2

    # The Micro-Drive cannot complete the task because it is not attached.
    MCL_DEV_NOT_ATTACHED = -3

    # Using a function from the library which the Micro-Drive does not support causes these errors.
    MCL_USAGE_ERROR = -4

    # The Micro-Drive is currently completing or waiting to complete another task.
    MCL_DEV_NOT_READY = -5

    # An argument is out of range or a required pointer is equal to NULL.
    MCL_ARGUMENT_ERROR = -6

    # Attempting an operation on an axis that does not exist in the Micro-Drive.
    MCL_INVALID_AXIS = -7

    # The handle is not valid.  Or at least is not valid in this instance of the DLL.
    MCL_INVALID_HANDLE = -8



class madLibCity_XY(XYStage):
    def __init__(self, mac_guiver, serial_number=None):
        self.handle = None
        self.serial_number = serial_number

        self.full_step_size_microns = 0
        self.micro_step_size_microns = 0
        self.encoder_resolution = 0
        self.max_velocity = 0
        self.max_velocity_two_axis = 0
        self.max_velocity_three_axis = 0
        self.min_velocity = 0
        super(madLibCity_XY, self).__init__(mac_guiver, frameName="MCL_XY", mm_name="MadLabXY")

    def load_device(self):
        self.mac_guiver.write_to_splash_screen("Loading MCL XY")
        try:
            # self.mmc.load_device(self.mm_name, "MCL_MicroDrive", "MicroDrive XY Stage")
            # self.mmc.initializeDevice(self.mm_name)

            mcl_lib_path = "c:/Program Files/Mad City Labs/Microdrive/MicroDrive"
            self.mcl_lib = ctypes.cdll.LoadLibrary(mcl_lib_path)
        except:
            self.mac_guiver.write_to_splash_screen("MCL_XY ini pb -> driver file (.dll) not found. Check MCL_controller.py")
            return False

        # One handle per DRIVER (and not per axis)
        try:
            if self.serial_number is not None :
                self.handle = self.mcl_lib.MCL_GetHandleBySerial(self.serial_number)
            else:
                self.handle = self.mcl_lib.MCL_InitHandle()
            if self.handle == 0:
                self.mac_guiver.write_to_splash_screen("MCL_XY ini pb -> error while getting the handle")
                return False
        except:
            self.mac_guiver.write_to_splash_screen("MCL_XY ini pb -> error while getting the handle")
            return False

        """
        bool MCL_DeviceAttached(unsigned int milliseconds, int handle)
        Function waits for a specified number of milliseconds then reports whether or not the Micro-Drive is attached. 

        Parameters:
        milliseconds 	[IN]	Indicates how long to wait.
        handle		[IN]	Specifies which Micro-Drive to communicate with.

        Return Value:
        Returns true if the specified Micro-Drive is attached and false if it is not.
        """
        wait_time_before_checking_ms = 50
        result = self.mcl_lib.MCL_DeviceAttached(wait_time_before_checking_ms, self.handle)

        if result is False:
            self.mac_guiver.write_to_splash_screen("MCL_XY ini pb -> Device attached test failed")
            return False

        """
        int MCL_GrabAllHandles() 
        Requests control of all of the attached Mad City Labs Micro-Drives that are not yet under control.
        
        Return Value:
        Returns the number of Micro-Drives currently controlled by this instance of the DLL.
        
        Notes:
        After calling this function use MCL_GetHandleBySerialNumber to get the handle of a specific device.
        
        Use MCL_NumberOfCurrentHandles and MCL_GetAllHandles to get a list of the handles acquired by this function.
        
        Remember that this function will take control of all of the attached Micro-Drives not currently under control.  
        Some of the aquired handles may need to be released if those Micro-Drives are needed in other applications.
        """
        # num_devices = self.mcl_lib.MCL_GrabAllHandles()

        """
        int MCL_GetAllHandles(int *handles, int size)
        Fills a list with valid handles to the Micro-Drives currently under the control of this instance of the DLL.

        Parameters:
        handles	[IN/OUT]	Pointer to an array of  'size' integers.
        size	[IN] 		Size of the 'handles' array

        Return Value:
        Returns the number of valid handles put into the 'handles' array.
        """




        """
        int MCL_GetHandleBySerial(short serial)
        Searches Micro-Drives currently controlled for a Micro-Drive whose serial number matches 'serial'.
        
        Parameters:
        serial	[IN] 	Serial # of the Micro-Drive whose handle you want to lookup.
        
        Return Value:
        Returns a valid handle or returns 0 to indicate failure.
        
        Notes:
        Since this function only searches through Micro-Drives which the DLL is controlling, MCL_GrabAllHandles() or multiple calls to MCL_(Init/Grab)Handle should be called before using this function.
        """

        # if self.serial_number_x is not None:
        #     self.handle_x = self.mcl_lib.MCL_GetHandleBySerial(self.serial_number_x)
        # if self.serial_number_y is not None :
        #     self.handle_y = self.mcl_lib.MCL_GetHandleBySerial(self.serial_number_y)




        # https://stackoverflow.com/questions/43317409/ctypes-argumenterror-dont-know-how-to-convert-parameter
        """
        int 	MCL_MDMoveThreeAxesR(
		int axis1, double velocity1, double distance1, int rounding1,
		int axis2, double velocity2, double distance2, int rounding2,
		int axis3, double velocity3, double distance3, int rounding3,
		int handle)
		"""
        self.mcl_lib.MCL_MDMoveThreeAxesR.argtypes = [ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_int,
                                                      ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_int,
                                                      ctypes.c_int]

        self.mcl_lib.MCL_MDMoveThreeAxes.argtypes = [ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_int,
                                                      ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_int,
                                                      ctypes.c_int]

        #         int MCL_MDCurrentPositionM(unsigned int axis, int * microSteps, int  handle)
        self.mcl_lib.MCL_MDCurrentPositionM.argtypes = [ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_int,
                                                      ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_int,
                                                      ctypes.c_int]

        """
        int MCL_MDCurrentPositionM(unsigned int axis, int *microSteps, int handle)
        """
        self.mcl_lib.MCL_MDCurrentPositionM.argtypes = [ctypes.c_uint, ctypes.POINTER(ctypes.c_int), ctypes.c_int]

        """
        int MCL_GetFullStepSize(double *stepSize, int handle)
        Allows the program to query the size of a full step.  This information combined with the micro step size
        from MCL_MDInformation can be used to determine the number of micro steps per full step.  Some applications may wish to stop on full steps or half steps.  The rounding arguments for the move funcitons will round to either full, half, or nearest step.
        
        Parameters:
        stepSize 	[IN/OUT] Set to the size of a full step.
        handle	[IN]	Specifies which Micro-Drive to communicate with.
        
        Return Value:
        Returns MCL_SUCCESS or the appropriate error code.
        """
        self.mcl_lib.MCL_GetFullStepSize.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int]

        """
        int MCL_MDInformation(
		double* encoderResolution,
		double* stepSize,
		double* maxVelocity,
		double* maxVelocityTwoAxis,
		double* maxVelocityThreeAxis,
		double* minVelocity,
		int handle)
		
        Gather Information about the resolution and speed of the Micro-Drive.
        
        Parameters:
        encoderResolution	[IN/OUT]  Set to the encoder resolution in um.
        stepSize		  	[IN/OUT]  Set to the size of a single step in mm.
        maxVelocity		[IN/OUT]  Set to the maximum velocity in mm of a single axis move.
        maxVelocityTwoAxis	[IN/OUT]  Set to the maximum velocity in mm of a two axis move.
        maxVelocityThreeAxis	[IN/OUT]  Set to the maximum velocity in mm of a three axis move.
        minVelocity		[IN/OUT]  Set to the minimum velocity in mm of a move.
        handle			[IN]	Specifies which Micro-Drive to communicate with.
        
        Return Value:
        Returns MCL_SUCCESS or the appropriate error code.
        """
        self.mcl_lib.MCL_MDInformation.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.c_int]

        self.get_info()



        return True

    def get_info(self):
        full_step_size_mm = ctypes.c_double(float(self.full_step_size_microns))
        encoder_resolution = ctypes.c_double(float(self.encoder_resolution))
        micro_step_size_mm = ctypes.c_double(float(self.micro_step_size_microns))
        max_velocity = ctypes.c_double(float(self.max_velocity))
        max_velocity_two_axis = ctypes.c_double(float(self.max_velocity_two_axis))
        max_velocity_three_axis = ctypes.c_double(float(self.max_velocity_three_axis))
        min_velocity = ctypes.c_double(float(self.min_velocity))

        # Get information on step size and microstep size.
        self.mcl_lib.MCL_GetFullStepSize(ctypes.byref(full_step_size_mm), self.handle)
        self.mcl_lib.MCL_MDInformation(ctypes.byref(encoder_resolution), ctypes.byref(micro_step_size_mm), ctypes.byref(max_velocity), ctypes.byref(max_velocity_two_axis),  ctypes.byref(max_velocity_three_axis), ctypes.byref(min_velocity), self.handle)

        self.full_step_size_microns = full_step_size_mm.value * 1000
        self.encoder_resolution = encoder_resolution.value
        self.micro_step_size_microns = micro_step_size_mm.value * 1000
        self.max_velocity = max_velocity.value
        self.max_velocity_two_axis = max_velocity_two_axis.value
        self.max_velocity_three_axis = max_velocity_three_axis.value
        self.min_velocity = min_velocity.value


    def move_absolute(self, pos_micron):
        # self.mmc.setXYPosition(self.mm_name, self.posMicron[0], self.posMicron[1])
        """
         int 	MCL_MDMoveThreeAxes(
		int axis1, double velocity1, double distance1,
		int axis2, double velocity2, double distance2,
		int axis3, double velocity3, double distance3,
		int handle)
        :param pos_micron:
        :return:
        """
        result = self.mcl_lib.MCL_MDMoveThreeAxes(1, self.speed[0] / 1000.0, pos_micron[0] / 1000.0, 0, 2, self.speed[1] / 1000.0, pos_micron[1] / 1000.0, 0, 0, 0, 0, 0, self.handle)
        return result


    def move_relative(self, pos_micron):
        # self.mmc.setRelativeXYPosition(self.mm_name, pos_micron[0], pos_micron[1])
        """

        //MCL_MDMoveThreeAxesR -> en relatif.

         int 	MCL_MDMoveThreeAxesR(
		int axis1, double velocity1, double distance1, int rounding1,
		int axis2, double velocity2, double distance2, int rounding2,
		int axis3, double velocity3, double distance3, int rounding3,
		int handle)
Standard movement function.  Acceleration and deceleration ramps are generated for the specified motion. In some cases when taking smaller steps the velocity parameter may be coerced to its maximum achievable value. The maximum and minimum velocities can be found using MCL_MDInformation. The maximum velocity differs depending on how many axes are commaned to move.

Parameters:
axis(1/2/3)	[IN]	Which axis to move.  (M1=1, M2=2, M3=3, M4=4, M5=5, M6=6) If using a Micro-Drive1,
			this argument is ignored.
velocity(1/2/3)	[IN]	Speed in mm/sec.
distance(1/2/3)	[IN]	Distance in mm to move the stage.  Positive distances move the stage toward its forward limit 				switch.  Negative distances move it toward its reverse limit switch.  A value of 0.0 will result in 				the axis not moving.
rounding(1/2/3)	[IN]	Determines how to round the distance parameter:
				0 - Nearest microstep.
				1 - Nearest full step.
				2 - Nearest half step.
handle		[IN]	Specifies which Micro-Drive to communicate with.

Return Value:
Returns MCL_SUCCESS or the appropriate error code.

Notes:
Care should be taken not to access the Micro-Drive while the microstage is moving for any reason other than stopping it. Doing so will adversely affect the internal timers of the Micro-Drive which generate the required step pulses for the specified movement.


        :param pos_micron:
        :return:
        """
        result = self.mcl_lib.MCL_MDMoveThreeAxesR(1, self.speed[0] / 1000.0, pos_micron[0] / 1000.0, 0, 2, self.speed[1] / 1000.0, pos_micron[1] / 1000.0, 0, 0, 0, 0, 0, self.handle)
        return result

    def get_position(self):
        """
        int MCL_MDCurrentPositionM(unsigned int axis, int *microSteps, int handle)
        Reads the number of microsteps taken since the beginning of the program.
        :return:
        """
        microSteps_X = ctypes.c_int(0)
        microSteps_Y = ctypes.c_int(0)

        self.mcl_lib.MCL_MDCurrentPositionM(1, ctypes.byref(microSteps_X), self.handle)
        self.mcl_lib.MCL_MDCurrentPositionM(2,  ctypes.byref(microSteps_Y), self.handle)

        # FIXME
        self.pos_abs_x_sv.set(str(microSteps_X.value * self.micro_step_size_microns))
        self.pos_abs_y_sv.set(str(microSteps_Y.value * self.micro_step_size_microns))



    def wait_for_device(self):
        #TODO loop
        result = -1
        while result != 0:
            result = self.mcl_lib.MCL_MicroDriveWait(self.handle)

    def stop(self):
        # TODO analyze status.
        status = ctypes.c_ushort(0)
        result = self.mcl_lib.MCL_MDStop(ctypes.addressof(status), self.handle)
        return result

    def close_device(self, params=None):
        self.mcl_lib.MCL_ReleaseAllHandles()

