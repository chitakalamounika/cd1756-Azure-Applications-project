Deployment Option Analysis: Azure VM vs Azure App Service

Summary
For this project, I chose to deploy the Flask Web Project on an Azure Virtual Machine (VM) instead of an App Service.

Reason:
A VM gives full control over the OS, Python environment, SQL ODBC drivers, Nginx, and Gunicorn configuration — all of which were required to get the Flask + Azure SQL + ODBC integration working correctly.

If this were a production system with a managed CI/CD pipeline and auto-scaling requirements, Azure App Service would be a better choice.
But for this learning and debugging-intensive deployment, the VM approach made the most sense.

Azure Virtual Machine

Deploying on a VM provides complete control over the environment. I could manually install all necessary system packages, including the Microsoft ODBC Driver 18 for SQL Server, which was essential for connecting the Flask application to the Azure SQL Database using pyodbc. On a VM, I had full root access to install Python, configure virtual environments, set up Gunicorn as the WSGI server, and use Nginx as a reverse proxy.

The main advantage of a VM is that I can manage every layer of the stack — operating system, dependencies, network rules, and application services. This makes troubleshooting much easier since I can directly inspect logs using commands like journalctl, check configurations, and control startup behavior with systemd.

However, this level of control comes with higher maintenance. The VM requires manual OS updates, security patching, and scaling configuration. If more traffic arrives, I would have to create additional instances or configure a load balancer manually. Despite these challenges, the VM deployment provided a clear understanding of how a Flask app runs in a real server environment and gave me the flexibility to fix dependency issues that would have been difficult to handle in a managed platform.

Azure App Service

On the other hand, Azure App Service is a fully managed platform designed to simplify deployment. It automatically handles infrastructure management, scaling, and OS patching. Deploying through App Service would have been much faster — I could simply push the code via GitHub or use the az webapp up command to get a public URL within minutes.

App Service also integrates easily with Application Insights for monitoring and provides continuous deployment options through GitHub Actions or Azure DevOps. However, because this Flask project requires native ODBC drivers for SQL Server, App Service would have been more complicated to configure. Installing these system-level dependencies is not straightforward unless I use a custom container image, which adds extra complexity.

While App Service is ideal for most production web apps due to its simplicity, scalability, and automation, it offers less control over the underlying system. For this specific project, that limited flexibility made it less suitable.

Reason for Choosing Azure VM

I chose to deploy the FlaskWebProject on an Azure Virtual Machine because it allowed me to:

Install and configure the Microsoft ODBC Driver 18 required by pyodbc.

Manually control all aspects of deployment — from Nginx setup to Gunicorn configuration.

Debug the application in detail using system logs and environment variables.

Gain hands-on experience managing a real-world production-like environment.

Using a VM helped me understand how Flask applications interact with Nginx, Gunicorn, Azure SQL, and Microsoft Authentication in a cloud environment. It also demonstrated the end-to-end process of hosting and managing a full-stack web application on Azure infrastructure.

When App Service Would Be Better

If this were a production application intended for continuous development, scaling, and automated deployment, I would choose Azure App Service instead. App Service is easier to maintain, supports seamless CI/CD pipelines, and automatically scales to handle more users. It eliminates most of the operational overhead, allowing developers to focus on code rather than infrastructure.

However, since this project was meant to show technical understanding of cloud deployment, networking, and dependency management, using a VM was the most practical and educational choice.

Deployed Architecture
Component	Description
Compute	Azure VM (vm-articlecms-moni4) — Ubuntu 22.04 LTS running Flask app with Nginx and Gunicorn
Database	Azure SQL Database: sql-cd1756-moni2 → database articlecms
Storage	Azure Blob Storage Account: stcd1756mounika, container: images
Authentication	Microsoft Entra ID (Azure AD) App Registration — MSAL login integrated
Logging	Application logs (/var/log/articlecms/app.log) and journalctl -u articlecms show login successes and failures
Networking	Port 80 open via NSG; Nginx reverse-proxies requests to Gunicorn on 127.0.0.1:8000
Deployment Steps (VM Path)

Created Resource Group

az group create -n rg-cd1756-mounika -l westus3


Created Azure VM

az vm create \
  -g rg-cd1756-mounika \
  -n vm-articlecms-moni4 \
  --image Ubuntu2204 \
  --size Standard_B1ms \
  --admin-username azureuser \
  --generate-ssh-keys


Installed Dependencies

sudo apt-get update
sudo apt-get install -y python3-venv python3-pip git nginx curl unixodbc-dev
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list | sudo tee /etc/apt/sources.list.d/msprod.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18


Cloned and Configured Flask App

git clone https://github.com/chitakalamounika/cd1756-Azure-Applications-project
cd cd1756-Azure-Applications-project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


Configured Gunicorn + systemd Service

/etc/systemd/system/articlecms.service

Includes all environment variables:

SQL_SERVER, SQL_DATABASE, SQL_USER_NAME, SQL_PASSWORD

CLIENT_ID, CLIENT_SECRET, TENANT_ID

BLOB_ACCOUNT, BLOB_CONTAINER, AZURE_STORAGE_CONNECTION_STRING

Configured Nginx

sudo nano /etc/nginx/sites-available/articlecms
# reverse proxy → 127.0.0.1:8000
sudo ln -s /etc/nginx/sites-available/articlecms /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx


Verified Service

sudo systemctl daemon-reload
sudo systemctl enable articlecms
sudo systemctl restart articlecms
sudo systemctl status articlecms --no-pager


Checked Logs

sudo journalctl -u articlecms -n 50 --no-pager

Authentication Setup

Microsoft Entra ID App Registration:

Redirect URI: http://<VM_PUBLIC_IP>/getAToken

Client ID: b56de121-32de-4130-987b-4364998b3ffa

Tenant ID: d93d0786-0aad-4792-93ba-6ea04036af73

Scope: User.Read

Sign-In Flow: Configured with MSAL (views.py)

Log Evidence:

Successful and failed logins appear in:

sudo journalctl -u articlecms --no-pager


Example:

INFO | User 'sqladminuser' logged in successfully
WARNING | Invalid login attempt (bad password) for 'unknown'
INFO | MS login successful for 'mounika@domain.com'

If Deployed via Azure App Service (Alternative)

If I had chosen App Service, steps would differ:

Push via az webapp up or GitHub Actions.

Configure App Settings for environment variables.

Skip manual ODBC install — use container with ODBC baked in.

Use App Service Log Stream for logs.

Benefits: quick setup, autoscale, managed runtime.

Drawback: limited native dependency control (ODBC, Nginx, Gunicorn customization).

Conclusion

For this project, Azure VM provided:

✅ Full control over native dependencies and drivers
✅ Transparent debugging and logging
✅ Complete visibility into the app stack (Nginx → Gunicorn → Flask → SQL)
✅ Hands-on learning of real-world deployment steps

If I were building a production-grade scalable web app, I would choose Azure App Service for easier management and scaling.
But for this hands-on implementation where I needed to install custom drivers, debug connection issues, and configure everything manually, the Azure VM was the right and most educational choice.

Final Deployment

URL: http://20.171.42.108/
Status: ✅ Running on Azure VM with Nginx, Gunicorn, Flask, and Azure SQL integration
