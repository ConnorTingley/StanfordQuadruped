import UDPComms
import numpy as np
import time
import xbox
from src.State import BehaviorState, State
from src.Command import Command
from src.Utilities import deadband, clipped_first_order_filter


class JoystickInterface:
    def __init__(
        self, config,
    ):
        self.config = config
        self.previous_gait_toggle = 0
        self.previous_state = BehaviorState.REST
        self.previous_hop_toggle = 0
        self.previous_activate_toggle = 0
        self.joy = xbox.Joystick()




    def get_command(self, state, do_print=False):
        if joy.connected():
            msg = self.udp_handle.get()
            command = Command()
            
            ####### Handle discrete commands ########
            # Check if requesting a state transition to trotting, or from trotting to resting
            gait_toggle = joy.rightBumper()
            command.trot_event = (gait_toggle == 1 and self.previous_gait_toggle == 0)

            # Check if requesting a state transition to hopping, from trotting or resting
            hop_toggle = joy.X()
            command.hop_event = (hop_toggle == 1 and self.previous_hop_toggle == 0)            
            
            activate_toggle = joy.leftBumper()
            command.activate_event = (activate_toggle == 1 and self.previous_activate_toggle == 0)

            # Update previous values for toggles and state
            self.previous_gait_toggle = gait_toggle
            self.previous_hop_toggle = hop_toggle
            self.previous_activate_toggle = activate_toggle

            ####### Handle continuous commands ########
            x_vel = joy.leftX() * self.config.max_x_velocity
            y_vel = joy.leftY() * -self.config.max_y_velocity
            command.horizontal_velocity = np.array([x_vel, y_vel])
            command.yaw_rate = joy.rightX() * -self.config.max_yaw_rate

            message_dt = joy.refreshDelay

            pitch = joy.rightY() * self.config.max_pitch
            deadbanded_pitch = deadband(
                pitch, self.config.pitch_deadband
            )
            pitch_rate = clipped_first_order_filter(
                state.pitch,
                deadbanded_pitch,
                self.config.max_pitch_rate,
                self.config.pitch_time_constant,
            )
            command.pitch = state.pitch + message_dt * pitch_rate

            height_movement = joy.dpadUp() - joy.dpadDown()
            command.height = state.height - message_dt * self.config.z_speed * height_movement
            
            roll_movement = joy.dpadRight() - joy.dpadLeft()
            command.roll = state.roll + message_dt * self.config.roll_speed * roll_movement

            return command

        else :
            print("Xbox Controller Not Connected")
            return Command()


    def set_color(self, color):
        print("Color change does not work with Xbox controller")