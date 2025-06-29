# 🥑 Web AVOCADO Deployment Guide for ReclaimHosting

## 📁 File Structure to Upload

Create this folder structure on your ReclaimHosting account:

```
public_html/avocado/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .htaccess              # Web server configuration
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Main page
│   └── progress.html      # Progress page
└── static/ (optional)
    └── (any additional CSS/JS files)
```

## 🚀 Step-by-Step Deployment Instructions

### Step 1: Access Your ReclaimHosting Account
1. **Log into cPanel** on your ReclaimHosting account
2. **Open File Manager** or connect via **SSH/SFTP**

### Step 2: Create the Application Directory
1. **Navigate to** `public_html`
2. **Create folder** called `avocado`
3. **Upload all files** to `public_html/avocado/`

### Step 3: Set Up Python Environment
**Via SSH (Recommended):**
```bash
# Connect to your server
ssh yourusername@yourserver.reclaimhosting.com

# Navigate to your app directory
cd public_html/avocado

# Install Python dependencies
pip3 install --user -r requirements.txt

# Or if pip3 doesn't work:
python3 -m pip install --user -r requirements.txt
```

**Via cPanel Python App (Alternative):**
1. **Go to cPanel** → **Software** → **Python Apps**
2. **Create New App**:
   - Python Version: 3.8 or higher
   - Application Root: `/public_html/avocado`
   - Application URL: `yoursite.com/avocado`
3. **Install dependencies** from requirements.txt

### Step 4: Configure Web Server
Create `.htaccess` file in `/public_html/avocado/`:

```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ app.py/$1 [QSA,L]

# Enable CGI for Python
Options +ExecCGI
AddHandler cgi-script .py

# Set environment variables
SetEnv PYTHONPATH /home/yourusername/.local/lib/python3.x/site-packages
```

### Step 5: Make app.py Executable
```bash
chmod +x app.py
```

### Step 6: Test the Application
1. **Visit**: `https://yoursite.com/avocado`
2. **Should see**: Web AVOCADO interface

## 🔧 Alternative Deployment Methods

### Method 1: Passenger (if available)
If ReclaimHosting supports Passenger:

1. **Create** `passenger_wsgi.py`:
```python
from app import app
application = app

if __name__ == "__main__":
    application.run()
```

2. **Configure** in cPanel → **Python Apps**

### Method 2: CGI Mode
Modify the first line of `app.py`:
```python
#!/usr/bin/python3
```

## 🌐 Accessing Your Web AVOCADO

Once deployed, you can access Web AVOCADO at:
- **URL**: `https://yoursite.com/avocado`
- **Features**: Same as desktop version but web-based!

## 🔍 Troubleshooting

### Common Issues:

**1. "Internal Server Error"**
- Check file permissions: `chmod 755` for directories, `chmod 644` for files
- Check error logs in cPanel

**2. "Python module not found"**
- Verify Python path in `.htaccess`
- Reinstall requirements: `pip3 install --user -r requirements.txt`

**3. "Permission denied"**
- Make sure `app.py` is executable: `chmod +x app.py`

**4. "Cannot import Flask"**
- Check Python version: `python3 --version`
- Install Flask specifically: `pip3 install --user Flask`

### Getting Help:
- **ReclaimHosting Support**: They're very helpful with Python deployments
- **Check cPanel Error Logs**: Look for specific error messages
- **Test locally first**: Make sure app works on your computer

## 📞 ReclaimHosting Support

If you need help:
1. **Contact ReclaimHosting support** - mention you're deploying a Flask app
2. **They can help with**:
   - Python environment setup
   - Module installation
   - Web server configuration

## 🎉 Success!

Once deployed, your Web AVOCADO will be accessible to:
- ✅ **You** from any device
- ✅ **Your team** members  
- ✅ **Other Venezuelan archive institutions**
- ✅ **Anyone you share the link with**

Perfect for collaborative Venezuelan cultural heritage metadata processing! 🇻🇪📚🥑