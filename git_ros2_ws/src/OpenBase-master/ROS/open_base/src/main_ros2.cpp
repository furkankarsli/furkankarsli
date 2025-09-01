#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose2_d.hpp>
#include <std_msgs/msg/float64.hpp>
#include <open_base/msg/movement.hpp>
#include <open_base/msg/velocity.hpp>

class OpenBaseController : public rclcpp::Node
{
public:
    OpenBaseController() : Node("open_base_controller")
    {
        // Initialize parameters
        this->declare_parameter("parameter.wheel.radius", 0.01905);
        radius = this->get_parameter("parameter.wheel.radius").as_double();

        // Initialize publishers
        v_left_command_ = this->create_publisher<std_msgs::msg::Float64>("left_joint_velocity_controller/command", 1);
        v_back_command_ = this->create_publisher<std_msgs::msg::Float64>("back_joint_velocity_controller/command", 1);
        v_right_command_ = this->create_publisher<std_msgs::msg::Float64>("right_joint_velocity_controller/command", 1);

        // Initialize subscribers
        command_subscriber_ = this->create_subscription<open_base::msg::Movement>(
            "command", 1, std::bind(&OpenBaseController::onCommandMessage, this, std::placeholders::_1));

        // Initialize timer
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(10), std::bind(&OpenBaseController::timerCallback, this));

        RCLCPP_INFO(this->get_logger(), "OpenBase controller initialized");
    }

private:
    double radius;
    open_base::msg::Velocity velocity;

    // Publishers
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr v_left_command_;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr v_back_command_;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr v_right_command_;

    // Subscribers
    rclcpp::Subscription<open_base::msg::Movement>::SharedPtr command_subscriber_;

    // Timer
    rclcpp::TimerBase::SharedPtr timer_;

    void onCommandMessage(const open_base::msg::Movement::SharedPtr input)
    {
        if (input->movement == open_base::msg::Movement::WHEEL) {
            velocity.v_left = input->wheel.v_left;
            velocity.v_back = input->wheel.v_back;
            velocity.v_right = input->wheel.v_right;
        } else {
            velocity.v_left = 0;
            velocity.v_back = 0;
            velocity.v_right = 0;
        }
    }

    void timerCallback()
    {
        // Publish wheel commands
        auto left_msg = std_msgs::msg::Float64();
        left_msg.data = velocity.v_left / radius;
        v_left_command_->publish(left_msg);

        auto back_msg = std_msgs::msg::Float64();
        back_msg.data = velocity.v_back / radius;
        v_back_command_->publish(back_msg);

        auto right_msg = std_msgs::msg::Float64();
        right_msg.data = velocity.v_right / radius;
        v_right_command_->publish(right_msg);
    }
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<OpenBaseController>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
