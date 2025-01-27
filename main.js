import {createPlayingBoard, playMove, updateBoardOnWin} from "./threeinarow.js";

// Displays an alert to the user.
function showMessage(message) {
    window.setTimeout(() => window.alert(message), 50);
}

function receiveMoves(playingBoard, websocket) {
    websocket.addEventListener("message", ({ data }) => {
        console.log("From Server: ", JSON.stringify(data, null, 2));
        const event = JSON.parse(data);
        switch (event.type) {
            case "INIT":
                // Creates the shareable link to join the game
                const shareInput = document.getElementById("share-link");
                const joinKey = event.join_key
                shareInput.value = window.location.origin + "/3-in-a-row-multiplayer/?join_key=" + joinKey;
                break;
            case "PLAY":
                // In case of PLAY event. Update the UI with the opponents move.
                playMove(playingBoard, event.player, event.column, event.row);
                break;
            case "WIN":
                const winningPosition = event.winning_pos
                updateBoardOnWin(playingBoard, winningPosition);
                showMessage(`Player ${event.player} wins!`)
                websocket.close(1000);
                break;
            case "ERROR":
                showMessage(event.message);
                break;
            default:
                throw new Error("Unknown event type " + event.type);
        }
    })
}
function sendMoves(playingBoard, websocket) {
    // Sends PLAY events to the server
    playingBoard.addEventListener("click", ({ target }) => {
        const column = target.dataset.column;
        const row = target.dataset.row;
        if (column === undefined || column === null) {
            return;
        }
        if (row === undefined || row === null) {
            return;
        }
        const event = {
            type: "PLAY",
            column: parseInt(column, 10),
            row: parseInt(row, 10),
        };
        websocket.send(JSON.stringify(event));
    });
}

function initGame(websocket) {
    websocket.addEventListener("open", () => {
        const params = new URLSearchParams(window.location.search);

        // Prepare the INIT event
        let event = { type: "INIT" };

        // Adds the join_key to the event if exists in the URL
        // If the URL contains a join_key then the player is the second player,
        // trying to join an initialized game
        if (params.has("join_key")) {
            event.join_key = params.get("join_key");
        }
        websocket.send(JSON.stringify(event));
    });
}

function getWebSocketServer() {
    if (window.location.host === "nikkcom.github.io") {
        return "wss://three-in-a-row-multiplayer-6c81864b3f27.herokuapp.com/"
    } else  if (window.location.host === "localhost:8000"){
        return "ws://localhost:8001";
    } else {
        throw new Error(`Unsupported host: ${window.location.host}`)
    }
}
window.addEventListener("DOMContentLoaded", () => {

    // Initialize the playing board.
    const playingBoard = document.querySelector(".board");
    createPlayingBoard(playingBoard);

    // Opens a websocket connection
    const websocket = new WebSocket(getWebSocketServer());

    // Register event handlers.
    initGame(websocket);
    receiveMoves(playingBoard, websocket);
    sendMoves(playingBoard, websocket);
})








