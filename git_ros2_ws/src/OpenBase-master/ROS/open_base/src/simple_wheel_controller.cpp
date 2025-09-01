#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <termios.h>
#include <unistd.h>
#include <iostream>

class SimpleWheelController : public rclcpp::Node
{
public:
    SimpleWheelController() : Node("simple_wheel_controller")
    {
        // Publisher for cmd_vel
        cmd_vel_pub_ = this->create_publisher<geometry_msgs::msg::Twist>(
            "cmd_vel", 10);

        // Timer for publishing commands
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(100),
            std::bind(&SimpleWheelController::publishCommands, this));

        // Initialize velocities
        linear_x_ = 0.0;
        linear_y_ = 0.0;
        angular_z_ = 0.0;

        // Setup terminal for key input
        setupTerminal();

        RCLCPP_INFO(this->get_logger(), "Simple Wheel Controller Started!");
        printInstructions();
    }

    ~SimpleWheelController()
    {
        // Restore terminal settings
        tcsetattr(STDIN_FILENO, TCSANOW, &old_termios_);
    }

private:
    void setupTerminal()
    {
        tcgetattr(STDIN_FILENO, &old_termios_);
        struct termios new_termios = old_termios_;
        new_termios.c_lflag &= ~(ICANON | ECHO);
        tcsetattr(STDIN_FILENO, TCSANOW, &new_termios);
    }

    void printInstructions()
    {
        std::cout << "\n=== OpenBase Simple Robot Controller ===" << std::endl;
        std::cout << "W/S = İleri/Geri" << std::endl;
        std::cout << "A/D = Sol/Sağ dönüş" << std::endl;
        std::cout << "Q/E = Sol/Sağ yan hareket" << std::endl;
        std::cout << "SPACE = Dur" << std::endl;
        std::cout << "X = Çıkış" << std::endl;
        std::cout << "========================================\n" << std::endl;
    }

    void publishCommands()
    {
        if (kbhit()) {
            char key = getchar();
            handleKeyInput(key);
        }

        auto twist_msg = geometry_msgs::msg::Twist();
        twist_msg.linear.x = linear_x_;
        twist_msg.linear.y = linear_y_;
        twist_msg.angular.z = angular_z_;
        cmd_vel_pub_->publish(twist_msg);
    }

    void handleKeyInput(char key)
    {
        const double speed = 1.0; // Robot hızı
        switch (key) {
            case 'w': case 'W': 
                linear_x_ = speed; 
                std::cout << "İleri: " << speed << std::endl;
                break;
            case 's': case 'S': 
                linear_x_ = -speed; 
                std::cout << "Geri: " << -speed << std::endl;
                break;
            case 'a': case 'A': 
                angular_z_ = speed; 
                std::cout << "Sol dönüş: " << speed << std::endl;
                break;
            case 'd': case 'D': 
                angular_z_ = -speed; 
                std::cout << "Sağ dönüş: " << -speed << std::endl;
                break;
            case 'q': case 'Q': 
                linear_y_ = speed; 
                std::cout << "Sol yan: " << speed << std::endl;
                break;
            case 'e': case 'E': 
                linear_y_ = -speed; 
                std::cout << "Sağ yan: " << -speed << std::endl;
                break;
            case ' ': 
                linear_x_ = 0.0; 
                linear_y_ = 0.0; 
                angular_z_ = 0.0; 
                std::cout << "Dur" << std::endl;
                break;
            case 'x': case 'X': 
                std::cout << "Çıkılıyor..." << std::endl;
                rclcpp::shutdown(); 
                break;
            default: 
                break;
        }
    }

    int kbhit()
    {
        struct timeval tv;
        fd_set rdfs;
        tv.tv_sec = 0;
        tv.tv_usec = 0;
        FD_ZERO(&rdfs);
        FD_SET(STDIN_FILENO, &rdfs);
        select(STDIN_FILENO + 1, &rdfs, nullptr, nullptr, &tv);
        return FD_ISSET(STDIN_FILENO, &rdfs);
    }

    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_pub_;
    rclcpp::TimerBase::SharedPtr timer_;
    
    double linear_x_;
    double linear_y_;
    double angular_z_;
    
    struct termios old_termios_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<SimpleWheelController>());
    rclcpp::shutdown();
    return 0;
}