let userData = {};
adminRequest = false;

function utf8ToBase64(str) {
  return btoa(unescape(encodeURIComponent(str)));
}

function base64ToUtf8(str) {
  return decodeURIComponent(escape(atob(str)));
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

async function metaDataMenu() {
  const response = await fetch("/api/admin/meta");
  const metadata = await response.json();

  document.querySelector(".td").innerHTML = `
              <h1 class="title">メタデータの編集</h1>
              <p class="head">
                  サイト全体の名前を見ることができます。
              </p>
    
              <form id="metaData">
                  メタデータID：
                  <input name="id" class="input" value="${
                    metadata.id
                  }" disabled />
                  サイトの名前：
                  <input name="name" class="input" value="${metadata.name}" />
                  認証で使うキャプチャの種類：
                  <select name="captcha_type" class="select is-fullwidth" />
                    <option value="NONE" selected>使わない</option>
                    <option value="RECAPTCHA">reCAPTCHA</option>
                    <option value="HCAPTCHA">hCAPTCHA</option>
                    <option value="TURNSTILE">Turnstile</option>
                  </select>
                  キャプチャのサイトキー：
                  <input name="captcha_sitekey" class="input" value="${
                    metadata.captcha_sitekey || ""
                  }" />
                  キャプチャのシークレットキー：
                  <input name="captcha_secret" type="password" class="input" value="${
                    metadata.captcha_secret || ""
                  }" />
                  <br>
                  <button class="button is-success is-fullwidth" id="metadataEditSubmit" type="submit">編集</button>
              </form>
  
                <hr>
    
              <button
                  class="button is-fullwidth is-primary mt-3"
                  onclick="mainmenu();"
              >
                  メインメニュー
              </button>
        `;

  document.getElementById("metaData").onsubmit = async (e) => {
    e.preventDefault();

    const submit = document.getElementById("metadataEditSubmit");

    submit.disabled = true;
    submit.classList.add("is-loading");

    const formData = new FormData(e.target);

    body = {
      id: metadata.id,
      name: formData.get("name"),
      captcha_type: formData.get("captcha_type"),
      captcha_sitekey: formData.get("captcha_sitekey"),
      captcha_secret: formData.get("captcha_secret"),
    };
    console.log(body);

    const response = await fetch(`/api/admin/meta/edit`, {
      method: "post",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify(body),
    });
    if (response.status == 200) {
      await response.text();

      bulmaToast.toast({
        message: "編集しました。",
        type: "is-success",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
      document.querySelector(".modal").className = "modal";
    } else {
      bulmaToast.toast({
        message: "失敗しました。",
        type: "is-danger",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
    }

    submit.disabled = false;
    submit.classList.remove("is-loading");
  };
}

async function deleteBoard(data) {
  let board = JSON.parse(data);
  document.querySelector(
    ".modal-card-title"
  ).textContent = `${board.name} を削除`;
  document.querySelector(".modal-card-body").textContent =
    "本当に削除しますか？";
  document.querySelector(".modal").className = "modal is-active";

  document.getElementById("primaryButton").onclick = async () => {
    const response = await fetch(`/api/admin/boards/${board.id}`, {
      method: "delete",
    });
    if (response.status == 200) {
      await response.text();

      bulmaToast.toast({
        message: "削除しました。",
        type: "is-success",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
      await boardsMenu();
      document.querySelector(".modal").className = "modal";
    } else {
      bulmaToast.toast({
        message: "失敗しました。",
        type: "is-danger",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
    }
  };
}

async function deleteThread(data, data2) {
  let thread = JSON.parse(data);
  document.querySelector(
    ".modal-card-title"
  ).textContent = `${thread.title} を削除`;
  document.querySelector(".modal-card-body").textContent =
    "本当に削除しますか？";
  document.querySelector(".modal").className = "modal is-active";

  document.getElementById("primaryButton").onclick = async () => {
    const response = await fetch(`/api/admin/threads/${thread.id}`, {
      method: "delete",
    });
    if (response.status == 200) {
      await response.text();

      bulmaToast.toast({
        message: "削除しました。",
        type: "is-success",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
      threads(data2);
      document.querySelector(".modal").className = "modal";
    } else {
      bulmaToast.toast({
        message: "失敗しました。",
        type: "is-danger",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
    }
  };
}

async function threads(data) {
  let board = JSON.parse(data);

  const response = await fetch(`/api/boards/${board.id}/threads`, {
    method: "get",
  });

  if (response.status != 200) {
    document.cookie = "session=; max-age=-1;";
    window.location.reload();
    return;
  }

  let threads = await response.json();

  document.querySelector(".td").innerHTML = `
            <h1 class="title">${board.name} のスレッド一覧</h1>
            <p class="head">
                スレッドを消すことができます。
            </p>

            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                        <th>スレッドID</th>
                        <th>スレ立て日</th>
                        <th>タイトル</th>
                        <th>レス数</th>
                        <th>スレ主(ID)</th>
                        <th>URL</th>
                        <th></th>
                        </tr>
                    </thead>
                    <tbody id="thread-table">
                    </tbody>
                </table>
            </div>
  
              <hr>
  
          <button
              class="button is-fullwidth is-primary mt-3"
              onclick="boardMenu('${board.id}');"
          >
              戻る
          </button>

            <button
                class="button is-fullwidth is-primary mt-3"
                onclick="mainmenu();"
            >
                メインメニュー
            </button>
    
            <button
                class="button is-fullwidth is-primary mt-3"
                onclick="metaDataMenu();"
            >
                メタデータ編集
            </button>
      `;

  threads.forEach((thread) => {
    let date = new Date(thread.created_at);

    let tr = document.createElement("tr");
    tr.innerHTML = `
      <th>${thread.id}</th>
      <th>${date.toLocaleString("ja-jp")}</th>
      <td>${thread.title}</td>
      <td>${thread.count}</td>
      <td><span style="color: green;"><b>${thread.name}</b></span> (${
      thread.account_id
    })</td>
      <td><a target="_blank" href="${window.location.protocol}//${
      window.location.host
    }/test/read.cgi/${thread.board}/${
      thread.timestamp
    }"><button class="button is-primary">スレッドへ</button></a></td>
      <td><button class="button is-danger" onclick="deleteThread(base64ToUtf8('${utf8ToBase64(
        JSON.stringify(thread)
      )}'), base64ToUtf8('${utf8ToBase64(data)}'))">削除</button></td>
    `;
    document.getElementById("thread-table").append(tr);
  });
}

async function editBoard(data) {
  let board = JSON.parse(data);

  document.querySelector(".td").innerHTML = `
            <h1 class="title">${board.name} の編集</h1>
            <p class="head">
                板名・名無し名・その他の変更ができます。
            </p>
  
            <form id="editBoard">
                板の名前：
                <input name="name" class="input" value="${board.name}" />
                板の名無し名：
                <input name="anonymous_name" class="input" value="${
                  board.anonymous_name
                }" />
                板の削除名：
                <input name="deleted_name" class="input" value="${
                  board.deleted_name
                }">
                スレッドのタイトルの最大文字数：
                <input type="number" min="0" name="subject_count" class="input" value="${
                  board.subject_count
                }">
                名前の最大文字数：
                <input type="number" min="0" name="name_count" class="input" value="${
                  board.name_count
                }">
                本文の最大文字数：
                <input type="number" min="0" name="message_count" class="input" value="${
                  board.message_count
                }">
                板の説明：
                <textarea name="head" class="textarea">${board.head}</textarea>
                <br>
                <button class="button is-success is-fullwidth" id="boardEditSubmit" type="submit">編集</button>
            </form>
  
              <hr>

            <button
                class="button is-fullwidth is-danger mt-3"
                onclick="deleteBoard(base64ToUtf8('${utf8ToBase64(data)}'));"
            >
                板を削除する
            </button>

              <hr>
  
            <button
                class="button is-fullwidth is-primary mt-3"
                onclick="boardMenu('${board.id}');"
            >
                戻る
            </button>
  
            <button
                class="button is-fullwidth is-primary mt-3"
                onclick="mainmenu();"
            >
                メインメニュー
            </button>
    
            <button
                class="button is-fullwidth is-primary mt-3"
                onclick="metaDataMenu();"
            >
                メタデータ編集
            </button>
      `;

  document.getElementById("editBoard").onsubmit = async (e) => {
    e.preventDefault();

    const submit = document.getElementById("boardEditSubmit");

    submit.disabled = true;
    submit.classList.add("is-loading");

    const formData = new FormData(e.target);

    body = {
      id: board.id,
      name: formData.get("name"),
      anonymous_name: formData.get("anonymous_name") || undefined,
      deleted_name: formData.get("deleted_name") || undefined,
      subject_count: formData.get("subject_count") || undefined,
      name_count: formData.get("name_count") || undefined,
      message_count: formData.get("message_count") || undefined,
      head: formData.get("head") || undefined,
    };

    const response = await fetch(`/api/admin/boards/${board.id}`, {
      method: "post",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify(body),
    });
    if (response.status == 200) {
      await response.text();

      bulmaToast.toast({
        message: "編集しました。",
        type: "is-success",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
      document.querySelector(".modal").className = "modal";
    } else {
      bulmaToast.toast({
        message: "失敗しました。",
        type: "is-danger",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
    }

    submit.disabled = false;
    submit.classList.remove("is-loading");
  };
}

async function boardMenu(boardId) {
  const response = await fetch(`/api/boards/${boardId}`, {
    method: "get",
  });

  if (response.status != 200) {
    document.cookie = "session=; max-age=-1;";
    window.location.reload();
    return;
  }

  let data = await response.text();
  let board = JSON.parse(data);

  document.querySelector(".td").innerHTML = `
          <h1 class="title">${board.name} の設定</h1>
          <p class="head">
              板に所属しているスレッドの操作や、板の操作ができます。
          </p>

          <button
              class="button is-fullwidth is-primary mt-3"
              onclick='threads(base64ToUtf8("${utf8ToBase64(data)}"));'
          >
              スレッドの管理
          </button>

          <button
              class="button is-fullwidth is-primary mt-3"
              onclick='editBoard(base64ToUtf8("${utf8ToBase64(data)}"));'
          >
              板を編集
          </button>

            <hr>

          <button
              class="button is-fullwidth is-primary mt-3"
              onclick="boardsMenu();"
          >
              戻る
          </button>

          <button
              class="button is-fullwidth is-primary mt-3"
              onclick="mainmenu();"
          >
              メインメニュー
          </button>
  
          <button
              class="button is-fullwidth is-primary mt-3"
              onclick="metaDataMenu();"
          >
              メタデータ編集
          </button>
    `;
}

async function createBoard() {
  document.querySelector(".td").innerHTML = `
              <h1 class="title">板の作成</h1>
              <p class="head">
                  板を作ることができます。
              </p>
    
              <form id="createBoard">
                  板のID(ディレクトリ名)：
                  <input name="id" class="input" />
                  板の名前：
                  <input name="name" class="input" />
                  板の名無し名：
                  <input name="anonymous_name" class="input" />
                  板の削除名：
                  <input name="deleted_name" class="input">
                  スレッドのタイトルの最大文字数：
                  <input type="number" min="0" name="subject_count" class="input">
                  名前の最大文字数：
                  <input type="number" min="0" name="name_count" class="input">
                  本文の最大文字数：
                  <input type="number" min="0" name="message_count" class="input">
                  板の説明：
                  <textarea name="head" class="textarea"></textarea>
                  <br>
                  <button class="button is-success is-fullwidth" id="boardCreateSubmit" type="submit">作成</button>
              </form>
    
                <hr>
    
              <button
                  class="button is-fullwidth is-primary mt-3"
                  onclick="boardsMenu();"
              >
                  戻る
              </button>
    
              <button
                  class="button is-fullwidth is-primary mt-3"
                  onclick="mainmenu();"
              >
                  メインメニュー
              </button>
      
              <button
                  class="button is-fullwidth is-primary mt-3"
                  onclick="metaDataMenu();"
              >
                  メタデータ編集
              </button>
        `;

  document.getElementById("createBoard").onsubmit = async (e) => {
    e.preventDefault();

    const submit = document.getElementById("boardCreateSubmit");

    submit.disabled = true;
    submit.classList.add("is-loading");

    const formData = new FormData(e.target);

    body = {
      id: formData.get("id"),
      name: formData.get("name"),
      anonymous_name: formData.get("anonymous_name") || undefined,
      deleted_name: formData.get("deleted_name") || undefined,
      subject_count: formData.get("subject_count") || undefined,
      name_count: formData.get("name_count") || undefined,
      message_count: formData.get("message_count") || undefined,
      head: formData.get("head") || undefined,
    };

    const response = await fetch(`/api/admin/boards/`, {
      method: "put",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify(body),
    });
    if (response.status == 200) {
      board = await response.json();

      bulmaToast.toast({
        message: "作成しました。",
        type: "is-success",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
      document.querySelector(".modal").className = "modal";

      submit.disabled = false;
      submit.classList.remove("is-loading");

      boardMenu(board.id);
    } else {
      bulmaToast.toast({
        message: "失敗しました。",
        type: "is-danger",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });

      submit.disabled = false;
      submit.classList.remove("is-loading");
    }
  };
}

async function boardsMenu() {
  const response = await fetch("/api/boards/", {
    method: "get",
  });

  if (response.status != 200) {
    document.cookie = "session=; max-age=-1;";
    window.location.reload();
    return;
  }

  let boards = await response.json();

  console.log(boards);
  let htmlData = "";
  boards.forEach((board) => {
    htmlData = `${htmlData}<button
              class="button is-fullwidth is-primary mt-3"
              onclick="boardMenu('${board.id}');"
          >
              ${board.name} (ID: ${board.id})
          </button>\n`;
  });

  document.querySelector(".td").innerHTML = `
          <h1 class="title">板設定</h1>
          <p class="head">
              板の一覧を確認したり、板を作成したり、編集することができます。
          </p>
  
          <div class="boards">
            <button
                class="button is-fullwidth is-primary mt-3"
                onclick="createBoard();"
            >
              板を作成
            </button>
            ${htmlData}
          </div>

            <hr>

          <button
              class="button is-fullwidth is-primary mt-3"
              onclick="mainmenu();"
          >
              メインメニュー
          </button>
  
          <button
              class="button is-fullwidth is-primary mt-3"
              onclick="metaDataMenu();"
          >
              メタデータ編集
          </button>
    `;
}

async function mainmenu() {
  const response = await fetch("/api/admin/me", {
    method: "get",
    headers: {
      x_mint_session: getCookie("session"),
    },
  });

  if (response.status != 200) {
    document.cookie = "session=; max-age=-1;";
    window.location.reload();
    return;
  }

  userData = await response.json();

  document.querySelector(".td").innerHTML = `
        <h1 class="title">メインメニュー</h1>
        <p class="head">
            現在<b>${userData.username}</b>としてログイン中です。
        </p>

        <hr>

        <button
            class="button is-fullwidth is-primary mt-3"
            onclick="boardsMenu();"
        >
            板設定
        </button>

        <button
            class="button is-fullwidth is-primary mt-3"
            onclick="metaDataMenu();"
        >
            メタデータ編集
        </button>
  `;
}

async function request(e) {
  e.preventDefault();
  const submit = document.getElementById("submit");

  submit.disabled = true;
  submit.classList.add("is-loading");

  const formData = new FormData(e.target);

  if (formData.get("password") != formData.get("password_l")) {
    bulmaToast.toast({
      message: "パスワードが一致しません",
      type: "is-danger",
      duration: 5000,
      dismissible: false,
      pauseOnHover: true,
      position: "top-right",
      closeOnClick: false,
      extraClasses: "popup",
      animate: { in: "fadeIn", out: "fadeOut" },
    });
    submit.disabled = false;
    return;
  }

  body = {
    username: formData.get("username"),
    password: formData.get("password"),
    adminRequestPassWord: formData.get("adminRequestPassword"),
  };
  const response = await fetch(`/api/admin/request`, {
    method: "post",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify(body),
  });
  try {
    const jsonData = await response.json();
    console.log(jsonData);

    submit.classList.remove("is-loading");

    if (response.status == 200) {
      bulmaToast.toast({
        message: "リクエスト完了しました。",
        type: "is-success",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });

      await mainmenu();
    } else {
      bulmaToast.toast({
        message: "ログインに失敗しました。",
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

async function login(e) {
  e.preventDefault();
  const submit = document.getElementById("submit");

  submit.disabled = true;
  submit.classList.add("is-loading");

  const formData = new FormData(e.target);
  body = {
    username: formData.get("username"),
    password: formData.get("password"),
  };
  const response = await fetch(`/api/admin/login`, {
    method: "post",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify(body),
  });
  try {
    const jsonData = await response.json();
    console.log(jsonData);

    submit.classList.remove("is-loading");

    if (response.status == 200) {
      bulmaToast.toast({
        message: "ログインしました。",
        type: "is-success",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });

      await mainmenu();
    } else {
      bulmaToast.toast({
        message: "ログインに失敗しました。",
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
  const response = await fetch("/api/admin/data");
  const jsonData = await response.json();

  if (!getCookie("session")) {
    if (jsonData.userCount == 0) {
      adminRequest = true;

      document.querySelector(".title").textContent =
        "管理者アカウントリクエスト";
      document.querySelector(".head").innerHTML =
        "Mintを利用するには、管理者アカウントをリクエストする必要があります。使用したいユーザー名、パスワード、そして<b>管理者リクエストパスワード</b>を入力してください。";
      document.querySelector(".formInput").innerHTML = `${
        document.querySelector(".formInput").innerHTML
      }\n
                    パスワード(確認)：<input
                    type="password"
                    name="password_l"
                    size="19"
                    class="input"
                    required
                    />
        \n管理者リクエストパスワード：<input
                    type="password"
                    name="adminRequestPassword"
                    size="19"
                    class="input"
                    required
                    />`;
      document.getElementById("submit").textContent = "リクエスト";
      document.getElementById("postForm").onsubmit = request;
    } else {
      document.getElementById("postForm").onsubmit = login;
    }
  } else {
    await mainmenu();
  }
});
