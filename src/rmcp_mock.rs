//! Mock implementation of the rmcp server components for testing
//! This file simulates the behavior of the real rmcp crate that would be used in production

use std::collections::HashMap;
use std::future::Future;
use std::pin::Pin;
use std::sync::{Arc, Mutex};
use anyhow::Result;

/// Mock Command Server
pub struct CommandServer {
    handlers: Arc<Mutex<HashMap<String, CommandHandler>>>,
}

/// Command handler function type
pub type CommandHandler = Box<dyn Fn(String, String) -> Pin<Box<dyn Future<Output = Result<String, anyhow::Error>> + Send>> + Send + Sync>;

/// Mock Server Handle
pub struct ServerHandle {
    server: Arc<CommandServer>,
}

impl CommandServer {
    /// Creates a new command server
    pub fn new() -> Self {
        CommandServer {
            handlers: Arc::new(Mutex::new(HashMap::new())),
        }
    }
    
    /// Starts the server, returning a handle
    pub async fn start(self) -> Result<ServerHandle> {
        Ok(ServerHandle {
            server: Arc::new(self),
        })
    }
    
    /// Registers a new command handler
    pub fn register_command<F, Fut>(&mut self, command: &str, handler: F)
    where
        F: Fn(String, String) -> Fut + Send + Sync + 'static,
        Fut: Future<Output = Result<String, anyhow::Error>> + Send + 'static,
    {
        let boxed_handler: CommandHandler = Box::new(move |context, request| {
            Box::pin(handler(context, request))
        });
        
        self.handlers.lock().unwrap().insert(command.to_string(), boxed_handler);
    }
    
    /// Handles a command
    pub async fn handle_command(&self, command: &str, context: &str, request: &str) -> Result<String, anyhow::Error> {
        let handlers = self.handlers.lock().unwrap();
        
        if let Some(handler) = handlers.get(command) {
            handler(context.to_string(), request.to_string()).await
        } else {
            Err(anyhow::anyhow!("Command not found: {}", command))
        }
    }
}

impl ServerHandle {
    /// Stops the server
    pub async fn stop(self) -> Result<()> {
        // In a real implementation, this would stop the server
        Ok(())
    }
}

/// Command Server Builder
pub struct CommandServerBuilder {
    server: CommandServer,
}

impl CommandServerBuilder {
    /// Creates a new command server builder
    pub fn new() -> Self {
        CommandServerBuilder {
            server: CommandServer::new(),
        }
    }
    
    /// Registers a command handler
    pub fn register_command<F, Fut>(&mut self, command: &str, handler: F) -> &mut Self
    where
        F: Fn(String, String) -> Fut + Send + Sync + 'static,
        Fut: Future<Output = Result<String, anyhow::Error>> + Send + 'static,
    {
        self.server.register_command(command, handler);
        self
    }
    
    /// Builds the server
    pub fn build(&self) -> Result<CommandServer> {
        Ok(CommandServer {
            handlers: self.server.handlers.clone(),
        })
    }
}

/// For convenience, create a namespace to mimic the real crate structure
pub mod server {
    pub use super::{CommandServer, CommandServerBuilder, ServerHandle};
}

/// Public API for the mock crate
pub mod rmcp {
    pub use super::server;
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_server_basic_functionality() {
        // Create a server
        let mut builder = CommandServerBuilder::new();
        
        // Register a command
        builder.register_command("echo", |_context: String, request: String| {
            Box::pin(async move { 
                Ok(format!("Echo: {}", request))
            })
        });
        
        let server = builder.build().unwrap();
        
        // Test the command
        let response = server.handle_command("echo", "test", "hello").await.unwrap();
        assert_eq!(response, "Echo: hello");
        
        // Test a non-existent command
        let result = server.handle_command("unknown", "test", "hello").await;
        assert!(result.is_err());
    }
}