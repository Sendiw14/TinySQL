//! TINYSQL engine. M0 skeleton: no SQL, storage or transaction behavior exists yet.
//! The only home of SQL semantics (master prompt, Section 4).

/// Milestone this build represents. Bumped only when a milestone gate passes with evidence.
pub const MILESTONE: &str = "M0";

#[cfg(test)]
mod tests {
    #[test]
    fn skeleton_reports_m0() {
        assert_eq!(super::MILESTONE, "M0");
    }
}
