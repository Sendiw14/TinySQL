//! TINYSQL CLI adapter. M0 skeleton only.

use std::process::ExitCode;

fn main() -> ExitCode {
    eprintln!(
        "tinysql {} ({} skeleton): no commands are implemented yet.",
        env!("CARGO_PKG_VERSION"),
        tinysql_engine::MILESTONE
    );
    ExitCode::FAILURE
}
