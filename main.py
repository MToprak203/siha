from MyUAVImageProcessor import Screen, process_result_package, MyUAVImageProcessor as imageProcessor
from MyUAVMovementProcessor import movement_result, MyUAVMovementProcessor as movementProcessor


def main():
    screen = Screen()
    image_processor = imageProcessor()
    movement_processor = movementProcessor()

    while screen.update_screen():
        if image_processor.begin_process:
            image_processor.process(screen.frame)
        movement_processor.track_target_locking()
        print(process_result_package)
        print(movement_result["movement_msg"])
        screen.display_screen()


if __name__ == "__main__":
    main()
