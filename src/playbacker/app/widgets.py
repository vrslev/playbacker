from datetime import datetime, timedelta
from typing import Callable, Union

import rich.repr
from rich.align import Align
from rich.box import Box
from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text
from textual._types import MessageTarget
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Footer as TextualFooter
from textual.widgets import NodeID, TreeClick, TreeControl, TreeNode

from playbacker.setlist import Setlist
from playbacker.song import Song


class Footer(TextualFooter):
    def render(self) -> RenderableType:
        super().render()
        assert self._key_text
        self._key_text.style = "dim blue"
        return self._key_text


class Header(Widget):
    def __init__(self, setlist: Setlist) -> None:
        super().__init__()
        self.setlist = setlist
        self.layout_size = 3

    def get_indicator(self) -> Text | None:
        return Text("●", style="yellow") if not self.setlist.preloaded else None

    def get_time(self) -> str:
        return datetime.now().time().strftime("%X")

    def render(self) -> RenderableType:
        table = Table.grid(padding=(0, 1), expand=True)
        table.add_column("status", justify="left", ratio=0, width=10)
        table.add_column("name", justify="center", ratio=1)
        table.add_column("clock", justify="right", width=8)
        table.add_row(self.get_indicator(), self.setlist.name, self.get_time())
        return Panel(table, style="blue")

    def on_mount(self) -> None:
        self.set_interval(1, callback=self.refresh)


_selected_box = Box(
    """\
┌   
│   
│   
│   
│   
│   
│   
└   
"""
)

_deselected_box = Box(
    """\
┌   
    
    
    
    
    
    
└   
"""
)


@rich.repr.auto
class SongListClick(Message, bubble=True):
    def __init__(self, sender: MessageTarget, song: Song) -> None:
        self.song = song
        super().__init__(sender)


class SongList(TreeControl[Song]):
    data: Setlist
    selected_node: TreeNode[Song] | None

    def __init__(self, setlist: Setlist) -> None:
        super().__init__(setlist.name, data=setlist, name=None)  # type: ignore
        self._tree.hide_root = True

    async def on_mount(self) -> None:
        await self.root.expand()

        for song in self.data.songs:
            await self.add(self.root.id, song.name, song)

        self.selected_node = self.nodes[NodeID(1)]

    def render_node(self, node: TreeNode[Song]) -> RenderableType:
        if node.id == self.root.id:
            return ""

        if self.selected_node and node.id == self.selected_node.id:
            box = _selected_box
            color = "bright_green"
        else:
            box = _deselected_box
            color = "bright_magenta"

        id = str(node.id)
        spaces = len(id) * " " + "  "

        tempo = str(node.data.tempo)

        title = f"[bold]{node.data.name}[/bold]"
        if node.data.artist:
            title += f" — {node.data.artist}"

        bits: tuple[str, ...] = (f"{id}. {title}", f"{spaces}{tempo}")
        label = Text.from_markup("\n".join(bits))

        style = Style(color=color, meta={"@click": f"click_label({node.id})"})
        return Panel(label, box=box, style=style, padding=(0, 2))

    async def handle_tree_click(self, message: TreeClick[Song]) -> None:
        await self.emit(SongListClick(self, message.node.data))

    def set_selected_song(self, song: Song) -> None:
        chosen = False
        for node in self.nodes.values():
            if node.data == song:
                chosen = True
                self.selected_node = node
        if not chosen:
            self.selected_node = None

        self.refresh()


StatusValueType = Union[str, bool, float, None]


def _get_pretty_value(value: StatusValueType) -> str:
    if isinstance(value, bool):
        if value is True:
            return "[bright_green italic]Enabled[/bright_green italic]"
        else:
            return "[bright_red italic]Disabled[/bright_red italic]"

    return str(value)


class StatusWidget(Widget):
    def __init__(self, title: str, initial_value: StatusValueType = None) -> None:
        self.title = title
        self.value = initial_value
        super().__init__()

    def render(self) -> RenderableType:
        value = _get_pretty_value(self.value)
        renderable = Align.center(value, vertical="middle", height=3)
        return Panel(renderable, title=self.title, highlight=True, width=25, height=5)

    def set(self, value: StatusValueType) -> None:
        self.value = value
        self.refresh()


class TimeWidget(StatusWidget):
    def __init__(self, time_getter: Callable[[], float]) -> None:
        self.time_getter = time_getter
        super().__init__(title="Time")

    def format_time(self, seconds: float) -> str:
        delta = timedelta(seconds=seconds)
        mm, ss = divmod(delta.total_seconds(), 60)
        _, mm = divmod(mm, 60)
        return "%02d:%02d" % (mm, ss)

    def get_value(self) -> str:
        seconds = self.time_getter()
        return self.format_time(seconds)

    def update(self) -> None:
        self.set(self.get_value())

    def on_mount(self) -> None:
        self.set_interval(1, callback=self.update)
        self.update()
