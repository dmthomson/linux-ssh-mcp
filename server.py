import paramiko
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
import os

# Initialize the MCP server with a friendly name
mcp = FastMCP("DynamicLinuxVMAdmin")

# --- SSH Client Management (New Approach) ---
# We'll create a new client for each tool call, or you could implement
# a more sophisticated connection pooling/caching mechanism based on host/user.
def get_ssh_client_dynamic(host: str, username: str, password: str = None, private_key_path: str = None):
    """Establishes and returns a new SSH client connection dynamically."""
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    # Be cautious with AutoAddPolicy in production; consider StrictHostKeyChecking
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        if private_key_path and os.path.exists(os.path.expanduser(private_key_path)):
            private_key = paramiko.RSAKey.from_private_key_file(os.path.expanduser(private_key_path))
            ssh_client.connect(hostname=host, username=username, pkey=private_key)
        elif password:
            ssh_client.connect(hostname=host, username=username, password=password)
        else:
            raise ValueError("Either 'password' or 'private_key_path' must be provided for SSH connection.")
        
        print(f"Successfully connected dynamically to {host}")
        return ssh_client
    except paramiko.AuthenticationException:
        print(f"Authentication failed for {username}@{host}. Check credentials.")
        return None
    except paramiko.SSHException as e:
        print(f"SSH connection error to {host}: {e}")
        return None
    except ValueError as e:
        print(f"Configuration error for {host}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while connecting to {host}: {e}")
        return None

# --- MCP Tools (Modified to accept connection details) ---

@mcp.tool()
async def execute_linux_command(
    command: str,
    host: str,
    username: str,
    password: str = None,
    private_key_path: str = None
) -> str:
    """
    Executes a shell command on the specified Linux VM and returns its output.
    Provide host, username, and either password or private_key_path.
    Example: `execute_linux_command("ls -l", host="192.168.1.100", username="user", password="mypass")`
    """
    client = get_ssh_client_dynamic(host, username, password, private_key_path)
    if not client:
        return "Error: Could not establish SSH connection to the Linux VM with provided credentials."

    try:
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        
        client.close() # Close connection after use (or manage via pool)

        if error:
            return f"Command executed with errors:\n{error}\nOutput:\n{output}"
        else:
            return output
    except Exception as e:
        return f"Error executing command '{command}': {e}"

@mcp.tool()
async def read_file_content(
    file_path: str,
    host: str,
    username: str,
    password: str = None,
    private_key_path: str = None
) -> str:
    """
    Reads the content of a specified file on the Linux VM.
    Example: `read_file_content("/etc/os-release", host="192.168.1.100", username="user", private_key_path="~/.ssh/mykey")`
    """
    return await execute_linux_command(f"cat {file_path}", host, username, password, private_key_path)

@mcp.tool()
async def get_disk_usage(
    host: str,
    username: str,
    password: str = None,
    private_key_path: str = None
) -> str:
    """
    Retrieves and returns the disk usage information for the Linux VM.
    """
    return await execute_linux_command("df -h", host, username, password, private_key_path)

@mcp.tool()
async def list_directory_contents(
    path: str = ".",
    host: str,
    username: str,
    password: str = None,
    private_key_path: str = None
) -> str:
    """
    Lists the contents of a directory on the Linux VM. Defaults to current directory.
    """
    return await execute_linux_command(f"ls -l {path}", host, username, password, private_key_path)

@mcp.tool()
async def get_system_info(
    host: str,
    username: str,
    password: str = None,
    private_key_path: str = None
) -> str:
    """
    Retrieves basic system information about the Linux VM (e.g., OS, kernel).
    """
    return await execute_linux_command("uname -a && cat /etc/os-release", host, username, password, private_key_path)

# --- MCP Prompt (Modified to take connection details) ---
@mcp.prompt()
def dynamic_linux_chat_prompt(
    query: str,
    host: str,
    username: str,
    password: str = None,
    private_key_path: str = None
) -> list[base.Message]:
    """
    A prompt for interacting with a specific Linux VM using natural language.
    You must provide the host, username, and either password or private_key_path.
    The AI should use the available tools to answer questions about the VM.
    """
    return [
        base.SystemMessage(
            "You are an AI assistant that can interact with a specific Linux Virtual Machine. "
            "You have access to tools that can execute commands, read files, and get system information. "
            "When asked a question about the Linux VM, use the provided tools and the connection "
            "details (host, username, password/private_key_path) to get the necessary information. "
            "If a command requires sudo, preface it with 'sudo '. Be mindful of security and only execute commands "
            "that are relevant to the user's request. If you need to specify a path, make sure it's valid."
        ),
        base.UserMessage(query)
    ]

# Run the MCP server
if __name__ == '__main__':
    print("MCP server 'DynamicLinuxVMAdmin' starting...")
    mcp.run()