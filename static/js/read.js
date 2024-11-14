const cachedResponses = [];
let socketConnected = false;

let board = location.pathname.split("/")[3];
let key = location.pathname.split("/")[4];

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

    socket.emit("join_room", `board_${board}_thread_${key}`);
  });

  socket.on("global_count_event", (data) => {
    document.getElementById("globalViews").textContent = `${data.count}人`;
    document.getElementById("globalMaxViews").textContent = `/ ${data.max}人`;
  });

  socket.on("count_event", (data) => {
    document.getElementById("localViews").textContent = `${data.count}人`;
    document.getElementById("localMaxViews").textContent = `/ ${data.max}人`;
  });

  socket.on("thread_writed", (data) => {
    bulmaToast.toast({
      message: "レス + 1",
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

    cachedResponses.push(JSON.parse(data));
    console.log(cachedResponses);
    console.log(cachedResponses.length);
    refreshThread(cachedResponses);
  });
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

function formatDate(date) {
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  const seconds = String(date.getSeconds()).padStart(2, "0");
  const milliseconds = String(date.getMilliseconds()).padStart(3, "0");
  const week = ["日", "月", "火", "水", "木", "金", "土"];
  const w = week[date.getDay()];

  return `${yyyy}/${mm}/${dd}(${w}) ${hours}:${minutes}:${seconds}.${milliseconds}`;
}

async function refreshThread(responses) {
  const progressBar = document.getElementById("progress");

  const responsesElement = document.querySelector(".responses");

  let count = 0;
  const nodes = [];

  var returnDate = new Date();

  document.querySelector(".progress-bar").innerHTML =
    '<progress id="progress" class="progress is-link" value="0" max="2">Now Loading...</progress>';

  responses.forEach((response) => {
    count += 1;

    const node = document.createElement("div");
    node.classList.add("thread");

    const date = new Date(response.created_at);
    if (count == 1) {
      document.querySelector(".thread-title").textContent = response.title;
      returnDate = date;
    }
    node.innerHTML = `${count}：<span style="color: green;"><b>${
      response.name
    }</b></span>：${formatDate(date)} ID: ${response.account_id}`;

    const content = document.createElement("div");
    content.classList.add("content");
    content.innerHTML = response.content;
    node.append(content);

    nodes.push(node);

    progressBar.value = count;
  });

  responsesElement.innerHTML = "";
  nodes.forEach((node) => responsesElement.appendChild(node));
  progressBar.remove();

  if (!socketConnected) {
    connectSocketIO();
    socketConnected = true;
  }

  return returnDate;
}

async function post(e) {
  e.preventDefault();
  const submit = document.getElementById("submit");

  submit.disabled = true;
  submit.classList.add("is-loading");

  const formData = new FormData(e.target);
  body = {
    name: formData.get("name"),
    authKey: formData.get("authKey"),
    content: formData.get("content"),
  };
  response = await fetch(`/api/boards/${board}/threads/${key}`, {
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
        message: "スレッドに書き込みました。",
        type: "is-success",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
      e.target.querySelector("input[name=name]").value = "";
      e.target.querySelector("input[name=authKey]").value = "";
      e.target.querySelector("textarea[name=content]").value = "";
      submit.disabled = false;
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
      submit.disabled = false;
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
    submit.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  const progressBar = document.getElementById("progress");

  const response = await fetch(`/api/boards/${board}/threads/${key}`);
  const data = await response.text();
  const responses = JSON.parse(data);
  console.log(responses);
  progressBar.max = responses.length;
  responses.forEach((response) => {
    cachedResponses.push(response);
  });
  date = await refreshThread(responses);

  document.querySelector(".size").textContent = `${data.length}KB`;

  let nowDate = new Date();
  nowTime = (nowDate.getTime() - date.getTime()) / 1000 / 60;
  ikioi = (responses.length / nowTime) * 60 * 24;
  document.getElementById("ikioi").textContent = `勢い: ${ikioi}`;

  const postForm = document.getElementById("postForm");
  postForm.addEventListener("submit", post);
});
