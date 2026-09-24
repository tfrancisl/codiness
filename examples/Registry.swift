final class PluginRegistry {
    static let shared = PluginRegistry()

    private var plugins: [String: Plugin] = [:]

    private init() {}

    /// Registers a plugin. Returns false if the name is already taken.
    @discardableResult
    func register(_ plugin: Plugin) -> Bool {
        if plugins[plugin.name] != nil { return false }
        plugins[plugin.name] = plugin
        return true
    }
}
