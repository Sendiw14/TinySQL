//! TINYSQL loopback API adapter. M0 skeleton only: binds nothing, serves nothing.

use std::process::ExitCode;

fn main() -> ExitCode {
    eprintln!(
        "tinysql-server {} ({} skeleton): the local API is not implemented yet.",
        env!("CARGO_PKG_VERSION"),
        tinysql_engine::MILESTONE
    );
    ExitCode::FAILURE
}
