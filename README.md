# Linux SSH MCP: Dynamic Linux VM Management via AI Chat (MCP Server)

Linux SSH MCP AI is an **MCP (Model Context Protocol) server** that lets your AI chat client (like Cline or Claude Desktop) talk to remote Linux Virtual Machines (VMs) using natural language. Built with Python and `paramiko`, this server acts as a bridge, letting your AI run shell commands, read files, query system info, and more on your VMs just by asking questions in chat.

Unlike solutions that hardcode connection details, Linux SSH MCP AI focuses on **dynamic connections**. You provide the Linux VM's host, username, and authentication details (password or private key path) directly in your chat, making the server reusable for many VMs without needing code changes or restarts.

## 🚀 Features

- **Dynamic SSH Connections:** Connect to any Linux VM by providing host and login details in your AI chat.

- **Natural Language to Command:** Translate your conversational queries into executable Linux shell commands.

- **Core Linux Operations:**

Execute arbitrary shell commands (`execute_linux_command`).

- Read file contents (`read_file_content`).

- Check disk usage (`get_disk_usage`).

- List directory contents (`list_directory_contents`).

- Retrieve basic system information (`get_system_info`).

**Secure (with caveats):** Uses `paramiko` for robust SSH, supporting both password and private key authentication.

**Virtual Environment Ready:** Designed to run within a Python virtual environment for clean dependency management.

## 🛠️ Setup

### 1. Clone the Repository

```
git clone https://github.com/your-username/linux-bridge-ai.git
cd linux-bridge-ai

```

### 2. Set Up Python Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```

### 3. Install Dependencies

Install the required Python libraries (`mcp-sdk` and `paramiko`).

```
pip install mcp paramiko

```

### 4. Configure Your AI Client (e.g., Cline, Claude Desktop)

You'll need to tell your AI client where to find and how to run this MCP server.

**Important:** You **must** use the absolute path to your `server.py` file and the Python executable within your virtual environment.

#### **For Cline (VS Code Extension):**

1. $1
Locate your `cline_mcp_settings.json` file.

- **macOS:** `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

- **Windows:** `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

- **Linux:** `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

- **Tip:** In Cline, you can often find a "Configure MCP Servers" option that opens this file directly.

Add the following JSON configuration under the `mcpServers` object, replacing `/path/to/your/linux-bridge-ai` with your actual absolute path:

```
{
  "mcpServers": {
    "DynamicLinuxVMAdmin": {
      "command": "/path/to/your/linux-bridge-ai/venv/bin/python", // Adjust for Windows if needed (venv\\Scripts\\python.exe)
      "args": ["/path/to/your/linux-bridge-ai/server.py"],
      "description": "An MCP server for interacting with any Linux VM dynamically via SSH (using venv).",
      "prompts": [
        {
          "id": "dynamic_linux_chat_prompt",
          "name": "Dynamic Linux VM Chat (Manual Connect)",
          "description": "Chat with a Linux VM. You must provide host, username, and password/key details in your query."
        }
      ]
    }
  }
}

```

#### **For Claude Desktop:**

1. $1
2. $1
Add the following JSON configuration within the `servers` array, replacing `/path/to/your/linux-bridge-ai` with your actual absolute path:

```
{
  "servers": [
    {
      "name": "DynamicLinuxVMAdmin",
      "command": "/path/to/your/linux-bridge-ai/venv/bin/python", // Adjust for Windows if needed (venv\\Scripts\\python.exe)
      "args": ["/path/to/your/linux-bridge-ai/server.py"],
      "description": "An MCP server for interacting with any Linux VM dynamically via SSH.",
      "prompts": [
        {
          "id": "dynamic_linux_chat_prompt",
          "name": "Dynamic Linux VM Chat (Manual Connect)",
          "description": "Chat with a Linux VM. You must provide host, username, and password/key details in your query."
        }
      ]
    }
  ]
}

```

#### **For VS Code (Copilot Chat Agent Mode):**

1. Open VS Code.
2. Go to File > Preferences > Settings (or Code > Settings on macOS).
3. Go to File > Preferences > Settings (or Code > Settings on macOS).

Search for "MCP Servers" or directly open your settings.json file.
Add the following configuration under `"github.copilot.chat.agentMode.mcpServers"`, replacing `/path/to/your/linux-bridge-ai` with your actual absolute path:

```
"github.copilot.chat.agentMode.mcpServers": [
  {
    "name": "DynamicLinuxVMAdmin",
    "command": "/path/to/your/linux-bridge-ai/venv/bin/python", // Adjust for Windows if needed (venv\\Scripts\\python.exe)
    "args": ["/path/to/your/linux-bridge-ai/server.py"],
    "description": "An MCP server for interacting with any Linux VM dynamically via SSH.",
    "prompts": [
      {
        "id": "dynamic_linux_chat_prompt",
        "name": "Dynamic Linux VM Chat (Manual Connect)",
        "description": "Chat with a Linux VM. You must provide host, username, and password/key details in your query."
      }
    ]
  }
]

```

### 5. Start the MCP Server

After configuring your client, navigate back to your `linux-bridge-ai` directory in your terminal (with the virtual environment activated) and run the server:

```
source venv/bin/activate # (Or venv\Scripts\activate.bat on Windows)
python server.py

```

You should see a message indicating the MCP server is starting.

## 🚀 Usage

Once the MCP server is running and your AI client is configured, open your AI chat interface and select the "Dynamic Linux VM Chat (Manual Connect)" prompt (or similar, depending on your client's UI).

You **must** include the connection details (host, username, and either password or private key path) directly in your natural language query. The AI will then parse these details and use them to call the appropriate tools.

### Examples of Chat Queries:

**Using Password Authentication:**

> "Using the Linux VM at `192.168.1.105`, connect as `ubuntu` with password `myvm_password`, and tell me the current disk usage."

**Using Private Key Authentication:**

> "For the server `mydevvm.example.com`, logging in as `admin` with my private key located at `~/.ssh/id_rsa_dev`, what's the output of `uname -a`?"

**Executing a `sudo` command (if user has permissions):**

> "Connect to `testserver.local` as `sysadmin` using password `s3cr3tP4ss` and execute `sudo systemctl status apache2`."

**Reading a file:**

> "On `172.16.0.10` as user `backupuser` with key `~/.ssh/backup_key`, read the content of `/etc/os-release`."

## ⚠️ Security Considerations

**It's crucial to understand the security implications of this approach:**

- **Passing Credentials in Chat:** Sending passwords or private key paths directly in chat messages is **highly insecure**. This information could be logged by the AI provider, stored in your chat history, or exposed if your client's logs are compromised.

- **`paramiko.AutoAddPolicy()`:** For simplicity, the server uses `AutoAddPolicy()` which automatically adds new host keys to your `known_hosts` file. In a production environment, this is dangerous as it bypasses host key verification, making you vulnerable to Man-in-the-Middle (MITM) attacks. Consider using `paramiko.WarningPolicy()` or a strict host key checking mechanism.

- **`sudo` and Elevated Privileges:** If you allow the AI to execute commands with `sudo`, ensure the SSH user has minimal necessary privileges configured in `sudoers` on the target VM. Granting broad `sudo` access to an AI agent significantly increases risk.

- **Command Injection:** While the AI is expected to generate safe commands, directly exposing a raw `execute_linux_command` tool means a malicious or errant AI could potentially execute harmful commands. For production, more robust input validation and command sanitization would be essential.

**Recommendations for Enhanced Security:**

- **Environment Variables / Secrets Management:** For production deployments, store sensitive credentials (passwords, private keys) as environment variables on the machine running the MCP server, or integrate with a dedicated secrets management system (e.g., HashiCorp Vault).

- **SSH Agent Forwarding:** For private keys, configure SSH agent forwarding from your local machine to the MCP server's host. This way, the private key itself never resides on the server.

- **Role-Based Access Control (RBAC):** On your Linux VMs, configure your SSH users with precise permissions and `sudoers` rules, following the principle of least privilege.

- **Input Sanitization:** Implement stricter validation and sanitization for command inputs if you plan to extend this to untrusted or external users.

- **Language &amp; SSH Integration:**

**Linux SSH MCP AI:** Uses **Python** and the robust `paramiko` library to establish **direct SSH connections from the MCP server** to any specified Linux VM. This makes it ideal for true remote administration.

**Dynamic Connectivity:**

- **Linux SSH MCP AI:** Designed from the ground up for **dynamic host and credential input** through chat, making it reusable for managing multiple, different Linux VMs without server restarts or code changes.

**Command Execution Capabilities (`sudo`):**

- **Linux SSH MCP AI:** Can execute commands that require `sudo` (assuming the SSH user has appropriate `sudoers` configuration on the target VM and can execute without an interactive TTY). This is crucial for many administrative tasks.

**Tool Granularity:**

- **Linux SSH MCP AI:** Provides a set of defined tools (`read_file_content`, `get_disk_usage`, etc.) that guide the AI towards common administrative actions, making it easier for the AI to reason about its actions.

In essence, Linux SSH MCP AI is built for **more direct, flexible, and powerful remote Linux VM administration** through SSH, including the ability to run privileged commands.
## 🤝 Contributing

Contributions are welcome! If you have ideas for new features, improvements, or bug fixes, feel free to open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- The `mcp-sdk` for enabling AI tool integration.

- The `paramiko` library for robust SSH capabilities.

- The broader AI and open-source communities for continuous innovation.
