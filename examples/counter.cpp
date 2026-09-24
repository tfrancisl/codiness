#include <iostream>
#include <string>

class RequestCounter {
public:
    static RequestCounter &instance() {
        static RequestCounter counter;
        return counter;
    }

    void record(const std::string &route) {
        ++total_;
        std::cout << "request #" << total_ << " " << route << "\n";
    }

    int total() const { return total_; }

private:
    RequestCounter() = default;
    int total_ = 0;
};
