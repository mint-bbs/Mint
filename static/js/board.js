let board = location.pathname.split("/")[1];
let cachedThreads = [];

const AudioContext =
  window.AudioContext ||
  window.webkitAudioContext ||
  window.mozAudioContext ||
  window.oAudioContext ||
  window.msAudioContext;
const audioContext = new AudioContext();

let source = audioContext.createBufferSource();
let audioBuffer;

fetch("/static/sounds/notification.mp3")
  .then((response) => response.arrayBuffer())
  .then((arrayBuffer) => audioContext.decodeAudioData(arrayBuffer))
  .then((buffer) => {
    audioBuffer = buffer;
  })
  .catch((error) => console.error(error));

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

function playSound() {
  if (!audioBuffer) return;

  const source = audioContext.createBufferSource();
  source.buffer = audioBuffer;
  source.connect(audioContext.destination);
  source.start();
}

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

    socket.emit("join_room", `board_${board}`);
  });

  socket.on("global_count_event", (data) => {
    document.getElementById("globalViews").textContent = `${data.count}人`;
    document.getElementById("globalMaxViews").textContent = `/ ${data.max}人`;
  });

  socket.on("count_event", (data) => {
    document.getElementById("localViews").textContent = `${data.count}人`;
    document.getElementById("localMaxViews").textContent = `/ ${data.max}人`;
  });

  socket.on("thread_posted", (data) => {
    bulmaToast.toast({
      message: "スレッド + 1",
      type: "is-success",
      duration: 2000,
      dismissible: false,
      pauseOnHover: true,
      position: "top-right",
      closeOnClick: false,
      extraClasses: "popup",
      animate: { in: "fadeIn", out: "fadeOut" },
    });

    playSound();

    cachedThreads.splice(0, 0, JSON.parse(data));
    refreshThreads(cachedThreads);
  });

  socket.on("thread_position_changed", (data) => {
    bulmaToast.toast({
      message: "スレッド順更新",
      type: "is-success",
      duration: 2000,
      dismissible: false,
      pauseOnHover: true,
      position: "top-right",
      closeOnClick: false,
      extraClasses: "popup",
      animate: { in: "fadeIn", out: "fadeOut" },
    });

    playSound();

    cachedThreads = JSON.parse(data);
    refreshThreads(cachedThreads);
  });
}

async function refreshThreads(threads) {
  const threadsElement = document.getElementById("threadsList");
  threadsElement.innerHTML = "";
  let count = 0;
  threads.forEach((thread) => {
    count++;
    if (count > 50) {
      return;
    }
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
      bulmaToast.toast({
        message: "スレッドを書き込みました。3秒後に移動します。",
        type: "is-success",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-right",
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
        position: "top-right",
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
      position: "top-right",
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
  const name = getCookie("NAME");
  if (name == null) {
    document.getElementById("name").value = "";
  } else {
    document.getElementById("name").value = getCookie("NAME");
  }
  let response = await fetch(`/api/boards/${board}/threads`);
  let threads = await response.json();
  console.log(threads);
  await refreshThreads(threads);

  connectSocketIO();

  const postForm = document.getElementById("postForm");
  postForm.addEventListener("submit", post);
});
