from pywebio.output import clear, use_scope, put_scope
from pywebio.session import run_js, defer_call

from module.webui.utils import set_localstorage, WebIOTaskHandler


class Base:
    def __init__(self) -> None:
        self.alive = True
        self.visible = True
        self.task_handler = WebIOTaskHandler()
        defer_call(self.stop)

    def stop(self) -> None:
        self.alive = False
        self.task_handler.stop()


class Frame(Base):
    def __init__(self) -> None:
        super().__init__()
        self.page = "Home"

    # 切换侧边栏
    def init_aside(self, name: str = None) -> None:
        self.visible = True
        self.task_handler.remove_pending_task()
        clear("menu")
        clear("content")
        # 高亮按钮
        if name:
            self.activate_icon_button("aside", name)
            set_localstorage("aside", name)

    @use_scope("ROOT", clear=True)
    def _show(self) -> None:
        put_scope(
            "contents",
            [
                # 侧边栏
                put_scope("aside"),
                put_scope("menu"),
                put_scope("content")
            ],
        )

    @staticmethod
    def activate_icon_button(position, value) -> None:
        run_js(
            f"""
            $(".icon_button").removeClass("active");
            $("div[style*='--{position}-{value}--']").addClass("active");
        """
        )

    @staticmethod
    def pin_set_invalid_mark(keys) -> None:
        if isinstance(keys, str):
            keys = [keys]
        keys = ["_".join(key.split(".")) for key in keys]
        js = "".join(
            [
                f"""$(".form-control[name='{key}']").addClass('is-invalid');"""
                for key in keys
            ]
        )
        if js:
            run_js(js)
        # for key in keys:
        #     pin_update(key, valid_status=False)

    @staticmethod
    def pin_remove_invalid_mark(keys) -> None:
        if isinstance(keys, str):
            keys = [keys]
        keys = ["_".join(key.split(".")) for key in keys]
        js = "".join(
            [
                f"""$(".form-control[name='{key}']").removeClass('is-invalid');"""
                for key in keys
            ]
        )
        if js:
            run_js(js)
        # for key in keys:
        # pin_update(key, valid_status=0)
