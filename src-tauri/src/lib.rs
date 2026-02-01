mod backend;
mod tray;

use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }

      // Start the FastAPI backend
      if let Err(e) = backend::start_backend_server(&app.handle()) {
        eprintln!("Failed to start backend: {}", e);
        // Continue anyway - user might want to start backend manually
      }

      // Wait a moment for backend to start
      std::thread::sleep(std::time::Duration::from_secs(2));

      // Create system tray
      if let Err(e) = tray::create_tray(&app.handle()) {
        eprintln!("Failed to create system tray: {}", e);
      }

      // Handle window close event - minimize to tray instead of quitting
      if let Some(window) = app.get_webview_window("main") {
        let app_handle = app.handle().clone();
        window.on_window_event(move |event| {
          if let tauri::WindowEvent::CloseRequested { api, .. } = event {
            // Prevent default close behavior
            api.prevent_close();
            // Hide the window instead
            if let Some(win) = app_handle.get_webview_window("main") {
              let _ = win.hide();
            }
          }
        });
      }

      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
