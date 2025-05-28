import time
from typing import Literal, Optional

from env.classes.controller import Controller

# Classes
from env.classes.movement import Movement

# Config
from env.config import config
from env.func.autostart import startup_script

# Func
from env.func.DEBUG import dprint


def run_input_thread(mvmnt: Movement) -> None:
    """Thread to handle input from the controller."""
    while True:
        ctrllr = None  # Ensure ctrllr is always defined
        try:
            # Initialize the reset flag to True
            reset: bool = (
                True  # Flag to indicate if the reset command has already been executed
            )

            # Initialize the controller
            ctrllr = Controller()

            # Main loop to get input from the controller and execute corresponding movement
            while True:
                # Get input from the controller
                input_command: Optional[
                    Literal[
                        "step-backwards",
                        "step-forwards",
                        "turn-left",
                        "turn-right",
                        "sidestep-left",
                        "sidestep-right",
                        "lower",
                        "lift",
                        "normal",
                        "sit",
                        "RESET",
                        "HEARTBEAT",
                    ]
                ] = ctrllr.last_input
                elapsed_time_since_heartbeat: float = time.time() - (
                    ctrllr.last_heartbeat if ctrllr.last_heartbeat else 0
                )

                if elapsed_time_since_heartbeat > config.max_heartbeat_interval:
                    dprint(
                        f"{config.color_yellow}No heartbeat received for {elapsed_time_since_heartbeat:.2f} second(s), skipping next movement...{config.color_reset}"
                    )
                elif input_command is None:
                    dprint(
                        f"{config.color_yellow}[ NOTE ] No input received, waiting...{config.color_reset}"
                    )
                elif input_command == "RESET" and reset:
                    dprint(
                        f"{config.color_yellow}Received RESET command, stopping all movements...{config.color_reset}"
                    )
                    mvmnt.interrupt_movements()
                    mvmnt.normalize_all_legs(
                        duration_s=0.3
                    )  # Normalize all legs to their default position
                    reset = (
                        False  # Set the reset flag to True to prevent multiple resets
                    )
                elif input_command in mvmnt.function_map:
                    mvmnt.function_map[input_command]()
                    reset = True  # Reset the reset flag after executing the command
                    dprint(
                        f"{config.color_green}Finished executing command: {input_command}"
                    )

                # If the command is not valid, print an error message
                if not reset and input_command != "RESET":
                    dprint(
                        f"{config.color_red}Invalid command received: {input_command}{config.color_reset}"
                    )

                time.sleep(0.1)
        except Exception as e:
            dprint(
                f"{config.color_red}Error in input thread; Restarting! Error: {e}{config.color_reset}"
            )

            # Attempt to close the controller socket if it exists
            if ctrllr and ctrllr.sock:
                ctrllr.sock.close()  # Close the socket to free the port

            time.sleep(1)  # Sleep for a second before restarting the thread


def main() -> None:
    """Main function."""
    if config.debug:
        dprint(f"{config.color_green}Debug mode on!{config.color_reset}")

    mvmnt = Movement()

    # Execute startup script
    startup_script(mvmnt=mvmnt)
    run_input_thread(mvmnt=mvmnt)  # Start the input thread


if __name__ == "__main__":
    main()
