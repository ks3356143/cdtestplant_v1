import styles from "./styles.module.less"

const PopupYonghu = (props: { type: "case" | "demand" }) => {
    const content =
        props.type === "demand" ? (
            <a-space direction="vertical">
                <p>使用“^”和“@”来完成：</p>
                <p>
                    1. <a-tag color="red">“^”</a-tag>标注一个测试子项的开始
                </p>
                <p>
                    2. <a-tag color="red">“@”</a-tag>标识连接
                </p>
                <p>
                    3. 在测试子项名称紧跟着<a-tag color="red">“@”</a-tag>后面表示CPU项目的测试子项描述
                </p>
                <p>
                    4. 在测试子项步骤紧跟着<a-tag color="red">“@”</a-tag>后面表示测试子项步骤的预期
                </p>
                <p>例示：</p>
                <p>
                    <a-tag color="red">^</a-tag>测试子项名称<a-tag color="red">@</a-tag>测试子项描述(CPU项目)
                </p>
                <p>
                    换行表示步骤输入<a-tag color="red">@</a-tag>我是该步骤的预期
                </p>
                <p>例子样子：</p>
                <p>^测试子项1号@测试子项1号描述</p>
                <p>步骤1号@预期1号</p>
                <p>步骤2号@预期2号</p>
                <p>步骤3号@预期3号</p>
                <p>^测试子项2号@测试子项2号描述</p>
                <p>步骤1号@预期1号</p>
            </a-space>
        ) : (
            <a-space direction="vertical">
                <p>使用”@”：来完成步骤录入：</p>
                <p>1. 每一行代表一个用例步骤</p>
                <p>
                    2. <a-tag color="red">@</a-tag>用于连接测试用例步骤和预期结果
                </p>
                <p>例示：</p>
                <p>步骤1操作输入@步骤1的预期结果</p>
                <p>步骤2操作输入@步骤2的预期结果</p>
                <p>步骤3操作输入@步骤3的预期结果</p>
                <p>步骤4操作输入@步骤4的预期结果</p>
                <p>步骤5操作输入@步骤5的预期结果</p>
            </a-space>
        )
    return (
        <a-popover title="录入规则" position="left" key={props.type}>
            {{
                default: () => <icon-question-circle-fill class={styles.suffix} />,
                content: () => content
            }}
        </a-popover>
    )
}

export default PopupYonghu
