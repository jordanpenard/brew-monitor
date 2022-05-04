import abc


class MultiClientBase(metaclass=abc.ABCMeta):
    """Use this when the same test is needed for public, user or admin"""

    @abc.abstractmethod
    def _check_view(self, client):
        # TODO(tr) I need to find a better way to do that that can take other fixtures etc
        ...

    def test_public_view(self, public_client):
        self._check_view(public_client)

    def test_user_view(self, user_client):
        self._check_view(user_client)

    def test_admin_view(self, admin_client):
        self._check_view(admin_client)
