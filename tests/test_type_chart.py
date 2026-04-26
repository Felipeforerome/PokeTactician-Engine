import numpy as np
import pytest

from poketactician.config import NUMBER_OF_TYPES
from poketactician.type_chart import TYPE_CHART, TYPE_NAMES, get_matchup_multiplier, get_type_chart, get_type_index


class TestTypeChart:
    def test_type_chart_matches_configured_type_count(self) -> None:
        assert TYPE_CHART.shape == (NUMBER_OF_TYPES, NUMBER_OF_TYPES)
        assert len(TYPE_NAMES) == NUMBER_OF_TYPES

    def test_type_chart_is_read_only(self) -> None:
        with pytest.raises(ValueError):
            TYPE_CHART[0, 0] = 2.0

    def test_get_type_chart_returns_shared_immutable_chart(self) -> None:
        chart = get_type_chart()

        assert chart is TYPE_CHART
        assert not chart.flags.writeable

    def test_get_type_index_uses_stable_order(self) -> None:
        assert TYPE_NAMES[0] == "normal"
        assert TYPE_NAMES[-1] == "fairy"
        assert get_type_index("ghost") == 13

    def test_single_type_matchups(self) -> None:
        assert get_matchup_multiplier("fire", "grass") == 2.0
        assert get_matchup_multiplier("electric", "ground") == 0.0
        assert get_matchup_multiplier("normal", "ghost") == 0.0

    def test_dual_type_matchups(self) -> None:
        assert get_matchup_multiplier("fire", ("grass", "steel")) == 4.0
        assert get_matchup_multiplier("water", ("rock", "ground")) == 4.0
        assert np.isclose(get_matchup_multiplier("fighting", ("rock", "dark")), 4.0)

    def test_unknown_type_raises_clear_error(self) -> None:
        with pytest.raises(ValueError, match="Unknown Pokemon type"):
            get_type_index("light")
