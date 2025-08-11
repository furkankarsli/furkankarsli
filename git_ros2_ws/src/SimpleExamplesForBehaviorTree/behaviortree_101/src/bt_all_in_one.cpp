#include <rclcpp/rclcpp.hpp>
#include <behaviortree_cpp/bt_factory.h>
#include <behaviortree_cpp/loggers/bt_cout_logger.h>
#include <iostream>
#include <thread>

class KullaniciAksiyonu : public BT::SyncActionNode {
public:
    KullaniciAksiyonu(const std::string& name, const BT::NodeConfig& config)
        : BT::SyncActionNode(name, config) {}

    static BT::PortsList providedPorts() {
        return { BT::InputPort<std::string>("soru") };
    }

    BT::NodeStatus tick() override {
        auto soru = getInput<std::string>("soru");
        std::cout << soru.value() << " (E/H): ";
        
        char cevap;
        std::cin >> cevap;
        
        if(cevap == 'E' || cevap == 'e') {
            return BT::NodeStatus::SUCCESS;
        }
        return BT::NodeStatus::FAILURE;
    }
};

class DavranisAgaci : public rclcpp::Node {
public:
    DavranisAgaci() : rclcpp::Node("davranis_agaci") {
        BT::BehaviorTreeFactory factory;
        factory.registerNodeType<KullaniciAksiyonu>("Soru");
        
        tree_ = factory.createTreeFromText(R"(
            <root BTCPP_format="4" main_tree_to_execute="AnaAgac">
                <BehaviorTree ID="AnaAgac">
                    <Sequence name="AnaDizi">
                        <Soru soru="Kahvaltı yaptınız mı?"/>
                        <Soru soru="İşe gittiniz mi?"/>
                        <Soru soru="Egzersiz yaptınız mı?"/>
                    </Sequence>
                </BehaviorTree>
            </root>
        )");

        logger_ = std::make_shared<BT::StdCoutLogger>(tree_);
    }

    void calistir() {
        while(rclcpp::ok()) {
            tree_.tickOnce();
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    }

private:
    BT::Tree tree_;
    std::shared_ptr<BT::StdCoutLogger> logger_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<DavranisAgaci>();
    node->calistir();
    rclcpp::shutdown();
    return 0;
}