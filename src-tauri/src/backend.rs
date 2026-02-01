use std::process::{Child, Command};
use std::sync::Mutex;
use tauri::Manager;

static BACKEND_PROCESS: Mutex<Option<Child>> = Mutex::new(None);

pub fn start_backend_server(app_handle: &tauri::AppHandle) -> Result<(), String> {
    println!("Starting FastAPI backend server...");

    // Find Python executable
    let python_cmd = if cfg!(target_os = "windows") {
        "python"
    } else {
        "python3"
    };

    // Get the resource directory or current directory
    let app_dir = app_handle
        .path()
        .app_data_dir()
        .unwrap_or_else(|_| std::path::PathBuf::from("."));

    // In development, backend is in parent directory
    // In production, it would be bundled
    let backend_dir = if cfg!(debug_assertions) {
        std::env::current_dir()
            .unwrap()
            .parent()
            .unwrap()
            .to_path_buf()
    } else {
        app_dir.clone()
    };

    println!("Backend directory: {:?}", backend_dir);

    // Start uvicorn server
    let process = Command::new(python_cmd)
        .args(&[
            "-m",
            "uvicorn",
            "backend.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ])
        .current_dir(&backend_dir)
        .spawn()
        .map_err(|e| format!("Failed to start backend: {}", e))?;

    let pid = process.id();
    println!("✓ Backend started with PID: {}", pid);

    // Store process handle
    *BACKEND_PROCESS.lock().unwrap() = Some(process);

    Ok(())
}

pub fn stop_backend_server() {
    println!("Stopping backend server...");

    if let Some(mut process) = BACKEND_PROCESS.lock().unwrap().take() {
        match process.kill() {
            Ok(_) => println!("✓ Backend stopped"),
            Err(e) => eprintln!("Failed to stop backend: {}", e),
        }
    }
}

// Check if backend is running
pub fn is_backend_running() -> bool {
    BACKEND_PROCESS
        .lock()
        .unwrap()
        .as_mut()
        .map(|p| p.try_wait().ok().flatten().is_none())
        .unwrap_or(false)
}
