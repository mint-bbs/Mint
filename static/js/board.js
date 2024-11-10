let board = location.pathname.split("/")[1];
let cachedThreads = [];

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

function connectSocketIO() {
  const socket = io();

  socket.on("connect", () => {
    console.log("socket connect successful");
    socket.emit("join_room", `board_${bbs_id}`);
  });

  socket.on("thread_posted", (data) => {
    // cachedThreads.splice(0, 0);
  });
}

async function refreshThreads(threads) {
  const threadsElement = document.getElementById("threadsList");
  threadsElement.innerHTML = "";
  let count = 0;
  threads.forEach((thread) => {
    count++;
    cachedThreads.push(thread);
    let node = document.createElement("a");
    node.href = `/test/read.cgi/${thread.board}/${thread.timestamp}/`;
    node.textContent = `${count}: ${thread.title}(${thread.count}) `;
    threadsElement.append(node);
  });
}

async function post(e) {
  e.preventDefault();
  const submit = document.getElementById("submit");

  submit.disabled = true;
  submit.classList.add("is-loading");

  const formData = new FormData(e.target);
  body = {
    title: formData.get("title"),
    name: formData.get("name"),
    authKey: formData.get("authKey"),
    content: formData.get("content"),
  };
  response = await fetch(`/api/boards/${board}`, {
    method: "put",
    headers: {
      "content-type": "application/json",
      Cookie: `2ch_X=${getCookie("2ch_X")}`,
    },
    body: JSON.stringify(body),
  });
  try {
    jsonData = await response.json();
    console.log(jsonData);

    submit.classList.remove("is-loading");

    if (response.status == 200) {
      document.cookie = response.headers.cookie;

      bulmaToast.toast({
        message: "スレッドを書き込みました。3秒後に移動します。",
        type: "is-success",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-left",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
      setTimeout(function () {
        window.location.href = `/test/read.cgi/${board}/${jsonData.thread.timestamp}`;
      }, 3000);
    } else {
      bulmaToast.toast({
        message: jsonData.detail,
        type: "is-danger",
        duration: 5000,
        dismissible: true,
        pauseOnHover: true,
        position: "top-left",
        closeOnClick: true,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
      setTimeout(function () {
        submit.disabled = false;
      }, 1000);
    }
  } catch {
    bulmaToast.toast({
      message: "不明なエラーが発生しました。",
      type: "is-danger",
      duration: 5000,
      dismissible: true,
      pauseOnHover: true,
      position: "top-left",
      closeOnClick: true,
      extraClasses: "popup",
      animate: { in: "fadeIn", out: "fadeOut" },
    });
    setTimeout(function () {
      submit.disabled = false;
    }, 1000);
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  let response = await fetch(`/api/boards/${board}/threads`);
  let threads = await response.json();
  console.log(threads);
  await refreshThreads(threads);

  connectSocketIO();

  const postForm = document.getElementById("postForm");
  postForm.addEventListener("submit", post);
});
