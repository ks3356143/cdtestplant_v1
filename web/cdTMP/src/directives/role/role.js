import { useUserStore } from "@/store"

const role = (name) => {
    const userStore = useUserStore()
    return (userStore.role && userStore.role.includes(name)) || (userStore.role && userStore.role.includes("admin"))
}

export default role
