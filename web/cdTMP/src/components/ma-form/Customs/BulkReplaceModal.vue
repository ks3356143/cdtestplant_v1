<script lang="tsx">
import { defineComponent, ref } from "vue"
import { Modal, Form, FormItem, Input, Space, Button, Alert, Message } from "@arco-design/web-vue"
// 导入替换白名单
import handleSubmit from "./replaceFieldName"

export default defineComponent({
    name: "BulkPeplaceModal",
    props: {
        parentForm: { type: Object, required: true }
    },
    setup(props, { expose }) {
        // ref
        const formRef = ref()
        // refs
        const visible = ref(false)
        const formData = ref({
            originText: "",
            replaceText: ""
        })

        // inner-functions
        const submit = (record: { values: any; error: any }) => {
            handleSubmit(record, props.parentForm, formData)
        }

        // obj-functions
        const open = () => {
            // 如果已经打开则关闭，清空查询
            formData.value = {
                originText: "",
                replaceText: ""
            }
            visible.value = visible.value === true ? false : true
        }

        // expose
        expose({ open })
        return () => (
            <div class="bulk-replace-container">
                <Modal
                    draggable
                    unmount-on-close
                    title="替换当前页面文本"
                    width="500px"
                    v-model:visible={visible.value}
                    mask={false}
                    popup-container="#form-main-id"
                    modal-class="modal-container-custom-shadow"
                    modalAnimationName="fade"
                    footer={false}
                >
                    <Alert type="warning" class="mb-2">
                        无法替换时间等非文本字段
                    </Alert>
                    <Form model={formData.value} onSubmit={submit} ref={formRef}>
                        <FormItem
                            field="originText"
                            label="被替文本"
                            validate-trigger={["change", "blur"]}
                            rules={[
                                {
                                    required: true,
                                    message: "请输入查找和被替换的文本"
                                }
                            ]}
                        >
                            <Input placeholder="请输入被替换文本" v-model={formData.value.originText}></Input>
                        </FormItem>
                        <FormItem field="replaceText" label="被替换为" validate-trigger={["change", "blur"]}>
                            <Input placeholder="请输入替换的文本" v-model={formData.value.replaceText}></Input>
                        </FormItem>
                        <FormItem>
                            <Space>
                                <Button type="primary" html-type="submit">
                                    全部替换
                                </Button>
                                <Button onClick={() => formRef.value.resetFields()}>重置</Button>
                            </Space>
                        </FormItem>
                    </Form>
                </Modal>
            </div>
        )
    }
})
</script>

<style lang="less">
.modal-container-custom-shadow {
    box-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
}
</style>
