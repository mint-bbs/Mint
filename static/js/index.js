function connectSocketIO() {
  const socket = io();

  socket.on("connect", () => {
    bulmaToast.toast({
      message: "通知サーバーに接続しました。",
      type: "is-success",
      duration: 500,
      dismissible: false,
      pauseOnHover: true,
      position: "top-right",
      closeOnClick: false,
      extraClasses: "popup",
      animate: { in: "fadeIn", out: "fadeOut" },
    });

    socket.emit("join_room", "index");
  });

  socket.on("global_count_event", (data) => {
    document.getElementById("globalViews").textContent = `${data.count}人`;
    document.getElementById("globalMaxViews").textContent = `/ ${data.max}人`;
  });

  socket.on("count_event", (data) => {
    document.getElementById("localViews").textContent = `${data.count}人`;
    document.getElementById("localMaxViews").textContent = `/ ${data.max}人`;
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  const response = await fetch("/api/boards");
  const jsonData = await response.json();
  const boards = document.querySelector(".boards");
  jsonData.forEach((board) => {
    const button = document.createElement("a");
    button.classList.add("button");
    button.classList.add("is-success");
    button.classList.add("is-fullwidth");
    button.href = `/${board.id}`;
    button.textContent = board.name;
    boards.append(button);
  });

  await connectSocketIO();
});
