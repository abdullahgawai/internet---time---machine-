from app.models import SnapshotMetadata, MetadataDiff

class DiffService:
    @staticmethod
    def compute_diff(snap_a: SnapshotMetadata, snap_b: SnapshotMetadata) -> MetadataDiff:
        """Calculate structural differences between two snapshot metadata instances."""
        size_delta = snap_b.html_size_bytes - snap_a.html_size_bytes
        if snap_a.html_size_bytes > 0:
            size_pct = round(((snap_b.html_size_bytes - snap_a.html_size_bytes) / snap_a.html_size_bytes) * 100, 1)
        else:
            size_pct = 100.0 if snap_b.html_size_bytes > 0 else 0.0

        dom_delta = snap_b.dom_node_count - snap_a.dom_node_count
        img_delta = snap_b.image_count - snap_a.image_count
        res_delta = snap_b.external_resource_count - snap_a.external_resource_count

        # Determine mobile viewport transition
        if not snap_a.has_mobile_viewport and snap_b.has_mobile_viewport:
            mobile_transition = "Adopted Mobile Viewport (Responsive)"
        elif snap_a.has_mobile_viewport and snap_b.has_mobile_viewport:
            mobile_transition = "Both Mobile Ready"
        elif not snap_a.has_mobile_viewport and not snap_b.has_mobile_viewport:
            mobile_transition = "Desktop Only (Fixed Width/Table Layout)"
        else:
            mobile_transition = "Removed Mobile Viewport"

        fw_a = set(snap_a.detected_frameworks)
        fw_b = set(snap_b.detected_frameworks)

        frameworks_added = sorted(list(fw_b - fw_a))
        frameworks_removed = sorted(list(fw_a - fw_b))

        return MetadataDiff(
            ts1=snap_a.timestamp,
            ts2=snap_b.timestamp,
            html_size_delta=size_delta,
            html_size_change_pct=size_pct,
            dom_node_delta=dom_delta,
            image_count_delta=img_delta,
            external_resource_delta=res_delta,
            mobile_viewport_transition=mobile_transition,
            frameworks_added=frameworks_added,
            frameworks_removed=frameworks_removed
        )
