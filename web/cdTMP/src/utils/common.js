// 判断是否弹出层全屏
export const setModalSizeEvent = (callback) => {
    callback({ isFull: window.screen.width < 768, width: window.screen.width })
}
