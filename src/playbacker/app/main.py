from contextlib import suppress
from typing import NamedTuple, cast

from pydantic import ValidationError
from textual.app import App
from textual.binding import Binding
from textual.driver import Driver
from textual.reactive import Reactive
from textual.views._dock_view import DockView
from textual.widgets import ScrollView
from textual_inputs import TextInput
from textual_inputs.events import InputOnChange

from playbacker.app.widgets import (
    Footer,
    Header,
    SongList,
    SongListClick,
    StatusWidget,
    TimeWidget,
)
from playbacker.playback import Playback
from playbacker.player import Player
from playbacker.setlist import Setlist
from playbacker.settings import Settings
from playbacker.song import Song
from playbacker.tempo import Tempo


class Widgets(NamedTuple):
    tempo: StatusWidget
    guide: StatusWidget
    multitrack: StatusWidget
    time: TimeWidget


class PlaybackerApp(App):
    settings: Settings
    setlist: Setlist
    player: Player
    current_song: Song
    guide_enabled: Reactive[bool] = Reactive(True)
    custom_tempo: str | None = None
    song_list: SongList
    widgets: Widgets
    custom_tempo_input: TextInput

    def __init__(
        self,
        *,
        screen: bool = True,
        driver_class: type[Driver] | None = None,
        log: str = "",
        log_verbosity: int = 1,
        title: str = "Textual Application",
        settings: Settings,
        setlist: Setlist,
    ):
        self.settings = settings
        self.setlist = setlist
        self.setlist.preload_songs()

        super().__init__(
            screen=screen,
            driver_class=driver_class,
            log=log,
            log_verbosity=log_verbosity,
            title=title,
        )

    async def bind_local(
        self,
        primary: str,
        secondary: str,
        action: str,
        description: str = "",
        key_display: str | None = None,
    ):
        await self.bind(
            keys=primary,
            action=action,
            description=description,
            show=True,
            key_display=key_display,
        )
        await self.bind(
            keys=secondary,
            action=action,
            description=description,
            show=False,
            key_display=None,
        )

    async def _add_bindings(self):
        await self.bind_local("q", "й", "quit", "Quit")
        self.bindings.keys[" "] = Binding(
            " ", "play", "Play", show=True, key_display="Space"
        )
        await self.bind("left", "previous", "Previous", key_display="←")
        await self.bind("right", "next", "Next", key_display="→")
        await self.bind_local("r", "к", "reset", "Reset")
        await self.bind_local("g", "п", "toggle_guide", "Toggle Guide")
        await self.bind("enter", "submit", show=False)
        await self.bind("escape", "reset_focus", show=False)

    async def on_load(self):
        self.player = Player(Playback(self.settings))
        await self._add_bindings()

    def handle_song_list_click(self, message: SongListClick):
        self.change_song(message.song)

    async def _setup_body(self):
        self.custom_tempo_input = TextInput(title="Custom Tempo")
        await self.view.dock(self.custom_tempo_input, size=4)

        body = DockView()
        grid = await body.dock_grid(edge="right", gutter=(0, 1))

        grid.add_column("col", size=26)
        grid.add_row("row", size=6)
        grid.set_repeat(True, True)

        self.widgets = Widgets(
            tempo=StatusWidget("Tempo"),
            guide=StatusWidget("Guide", True),
            multitrack=StatusWidget("MultiTrack", True),
            time=TimeWidget(time_getter=self.player.time),
        )

        grid.place(*self.widgets)
        await self.view.dock(body, edge="right")

    async def on_mount(self):
        await self.view.dock(Header(self.setlist))
        await self.view.dock(Footer(), edge="bottom")

        self.song_list = SongList(self.setlist)
        await self.view.dock(ScrollView(self.song_list), edge="left", size=80)
        await self._setup_body()

        self.change_song(self.setlist.songs[0])

    def change_song(self, song: Song):
        self.player.pause()
        self.current_song = song
        self.guide_enabled = True
        self.widgets.tempo.set(str(song.tempo))
        self.song_list.set_selected_song(song)

    def action_play(self):
        if self.player.paused:
            self.player.start(self.current_song)
            self.player.toggle_guide(self.guide_enabled)
            self.widgets.multitrack.set(self.player.multitrack_enabled)
        else:
            self.player.pause()

    def action_previous(self):
        if song := self.setlist.previous(self.current_song):
            self.change_song(song)

    def action_next(self):
        song = self.setlist.next(self.current_song)
        self.change_song(song)

    def action_toggle_guide(self):
        self.guide_enabled = not self.guide_enabled

    def action_reset(self):
        self.player.reset()

    async def action_quit(self):
        self.player.stop()
        return await super().action_quit()

    def watch_guide_enabled(self, value: bool):
        if not self.player.started:
            return

        self.widgets.guide.set(value)
        self.player.toggle_guide(value)

    def handle_input_on_change(self, value: InputOnChange):
        self.custom_tempo = cast(TextInput, value.sender).value

    def _get_custom_tempo(self) -> None:
        if not self.custom_tempo:
            return

        parts = self.custom_tempo.split()
        if len(parts) != 3:
            return

        with suppress(ValidationError):
            return Tempo(bpm=parts[0], time_signature=parts[1], duration=parts[2])  # type: ignore

    async def action_submit(self):
        tempo = self._get_custom_tempo()

        if tempo is None:
            self.custom_tempo_input.border_style = "red"
            return

        self.change_song(Song.from_tempo(tempo))
        await self.action_reset_focus()

        self.custom_tempo_input.border_style = "blue"
        self.custom_tempo_input.value = ""

    async def action_reset_focus(self):
        await self.set_focus(self.song_list)
