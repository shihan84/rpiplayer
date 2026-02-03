# V-Player Enterprise - GitHub Codespaces Testing

## 🚀 Quick Start with Codespaces

This repository is fully configured for GitHub Codespaces, allowing you to test V-Player Enterprise in a cloud-based development environment without any local setup.

### 🌐 How to Use Codespaces

#### **Option 1: GitHub Web Interface**
1. Go to your repository on GitHub
2. Click the green **"Code"** button
3. Select **"Codespaces"** tab
4. Click **"Create codespace on main"**
5. Wait for the environment to build (2-3 minutes)

#### **Option 2: GitHub CLI**
```bash
# Create and open a codespace
gh codespace create -r shihan84/rpiplayer -b main
gh codespace ssh
```

#### **Option 3: VS Code**
1. Install [GitHub Codespaces extension](https://marketplace.visualstudio.com/items?itemName=GitHub.codespaces)
2. Open Command Palette (Ctrl+Shift+P)
3. Type **"Codespaces: Create New Codespace"**
4. Select repository and branch

### 🎯 What's Included in the Codespace

#### **🐳 Pre-configured Development Environment**
- **Python 3.9** with all dependencies installed
- **Redis** for caching and session management
- **FFmpeg** for video processing
- **All system dependencies** pre-installed
- **VS Code extensions** for Python development

#### **🚀 Automatic Setup**
- **Dependencies**: Automatically installed from `requirements.txt`
- **V-Player**: Application starts automatically
- **Image Builder**: Raspberry Pi image structure created
- **Web Interface**: Available at forwarded port 5005

#### **🔧 Development Tools**
- **Python Linting**: Flake8 and Black formatter
- **Debugging**: Python debugger configured
- **Git**: Version control ready
- **GitHub CLI**: Command-line GitHub access

### 🌐 Accessing the Application

#### **Web Interface**
1. Once codespace is ready, look for the **"Ports"** tab
2. Find port **5005** labeled **"V-Player Enterprise"**
3. Click the globe icon to open in browser
4. Or access via the provided URL (e.g., `https://*.github.dev`)

#### **Local Testing in Codespace**
```bash
# Check if application is running
curl http://localhost:5005

# View logs
tail -f logs/v-player.log

# Restart application
python3 app.py
```

### 🧪 Testing Features

#### **✅ Core Features to Test**
1. **Professional Broadcasting Interface**
   - Navigate to **"Outputs"** tab
   - Test video output configurations
   - Verify channel management

2. **Network Configuration**
   - Navigate to **"Network"** tab
   - Test WiFi scanning and connection
   - Verify Ethernet status
   - Test hotspot functionality

3. **Cloudflare Zero Trust**
   - In **"Network"** tab, find **"Cloudflare Zero Trust"** section
   - Test status checking
   - Generate setup instructions
   - Download setup script

4. **Real-time Monitoring**
   - Check system metrics
   - Verify network monitoring
   - Test WebSocket connections

#### **🔧 Advanced Testing**
```bash
# Test API endpoints
curl http://localhost:5005/api/system/info
curl http://localhost:5005/api/network/status
curl http://localhost:5005/api/cloudflare/status

# Test WebSocket connection
wscat -c ws://localhost:5005/socket.io/

# View system resources
htop
df -h
free -h
```

### 📱 Mobile Testing

#### **Responsive Design**
- Test on different screen sizes
- Use browser developer tools (Ctrl+Shift+M)
- Verify mobile compatibility

#### **Touch Interface**
- Test touch interactions
- Verify button sizes and spacing
- Check scroll behavior

### 🐛 Debugging in Codespaces

#### **VS Code Debugging**
1. Open `app.py`
2. Set breakpoints by clicking in the gutter
3. Press **F5** or go to **"Run and Debug"**
4. Select **"Python: Flask"** configuration

#### **Log Analysis**
```bash
# View application logs
tail -f logs/v-player.log

# View system logs
journalctl -f

# View Docker logs (if using container)
docker logs vplayer-enterprise
```

#### **Network Debugging**
```bash
# Check port status
netstat -tlnp | grep 5005

# Test connectivity
curl -v http://localhost:5005

# Check DNS
nslookup google.com
```

### 🚀 Building Raspberry Pi Image

#### **Generate Image Structure**
```bash
# Run the image builder
python3 build_rpi_image.py

# Check generated files
ls -la build/rpi-image/
```

#### **Verify Image Components**
```bash
# Check service files
cat build/rpi-image/etc/systemd/system/vplayer.service

# Check startup scripts
cat build/rpi-image/usr/local/bin/vplayer-setup.sh

# Check configuration files
cat build/rpi-image/etc/dhcpcd.conf.d/vplayer.conf
```

### 🔧 Customization

#### **Environment Variables**
Edit `.devcontainer/devcontainer.json` to modify:
- Python version
- Environment variables
- Port forwarding
- VS Code settings

#### **Additional Dependencies**
Add to `requirements.txt`:
```txt
# Additional Python packages
package-name==version
```

#### **System Dependencies**
Modify `.devcontainer/devcontainer.json` features:
```json
"features": {
  "ghcr.io/devcontainers/features/python:1": {
    "version": "3.10"
  },
  "ghcr.io/devcontainers/features/node:1": {}
}
```

### 📊 Performance Monitoring

#### **Resource Usage**
```bash
# CPU and memory usage
top
htop

# Disk usage
df -h

# Network usage
iftop
```

#### **Application Performance**
```bash
# Check Flask performance
curl -w "@curl-format.txt" http://localhost:5005/

# Monitor WebSocket connections
ss -tlnp | grep 5005
```

### 🔄 Syncing Changes

#### **Git Workflow**
```bash
# Stage changes
git add .

# Commit changes
git commit -m "Add feature via Codespaces"

# Push to repository
git push origin main
```

#### **File Sync**
- Files are automatically synced to your repository
- Use VS Code source control panel
- Changes persist across codespace sessions

### 🌐 Sharing Your Codespace

#### **Collaborative Development**
1. Go to GitHub repository
2. Click **"Code"** → **"Codespaces"**
3. Find your codespace
4. Click **"..."** → **"Share with collaborators"**

#### **Public Access**
- Create a public branch
- Share the codespace URL
- Collaborators can join your development session

### 📚 Additional Resources

#### **Documentation**
- [GitHub Codespaces documentation](https://docs.github.com/en/codespaces)
- [Dev Container specification](https://containers.dev/)
- [VS Code Remote Development](https://code.visualstudio.com/docs/remote/remote-overview)

#### **Troubleshooting**
- Check codespace logs in GitHub
- Restart codespace if needed
- Verify port forwarding settings
- Check resource limits

---

## 🎯 Ready to Test!

Your V-Player Enterprise is now ready for comprehensive testing in GitHub Codespaces. This environment provides:

✅ **Full application functionality**
✅ **Network configuration testing**
✅ **Cloudflare Zero Trust integration**
✅ **Raspberry Pi image building**
✅ **Professional broadcasting interface**
✅ **Real-time monitoring and metrics**

**Start testing now by creating a codespace and accessing the web interface!** 🚀
