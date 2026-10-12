"""Optional embedded Guava WebRTC view."""

from PySide6.QtCore import QUrl
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView


class GuavaWebView(QWebEngineView):
    """Display Guava client with scoped microphone permission."""

    def __init__(self) -> None:
        super().__init__()
        self.page().featurePermissionRequested.connect(self._grant_microphone)

    def open_code(self, code: str) -> None:
        """Open one configured WebRTC code."""
        self.setUrl(QUrl(f"https://app.goguava.ai/debug-webrtc?webrtc_code={code}"))

    def _grant_microphone(
        self,
        origin: QUrl,
        feature: QWebEnginePage.Feature,
    ) -> None:
        """Grant only microphone capture."""
        allowed = feature == QWebEnginePage.Feature.MediaAudioCapture
        policy = (
            QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
            if allowed
            else QWebEnginePage.PermissionPolicy.PermissionDeniedByUser
        )
        self.page().setFeaturePermission(origin, feature, policy)
