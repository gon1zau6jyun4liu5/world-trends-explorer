/**
 * Version and Build Information for World Trends Explorer
 * Automatically updated during build process
 */

window.AppVersion = {
    version: "1.1.0",
    branch: "feature/version-display-v1.1.0",
    buildDate: new Date().toISOString(),
    commit: "latest",
    environment: "development",
    
    // Get version string for display
    getVersionString() {
        return `v${this.version}`;
    },
    
    // Get branch display name
    getBranchDisplay() {
        return this.branch.replace("feature/", "").replace("bugfix/", "").replace("hotfix/", "");
    },
    
    // Get full version info
    getFullInfo() {
        return {
            version: this.version,
            branch: this.branch,
            buildDate: this.buildDate,
            commit: this.commit,
            environment: this.environment
        };
    },
    
    // Format for display in UI
    getDisplayInfo() {
        const branchDisplay = this.getBranchDisplay();
        return `${this.getVersionString()} • ${branchDisplay}`;
    },
    
    // Get build info for footer or debug
    getBuildInfo() {
        const buildDate = new Date(this.buildDate).toLocaleDateString();
        return `Built on ${buildDate} from ${this.branch}`;
    }
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.AppVersion;
}