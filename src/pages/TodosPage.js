import { Stack } from "@mui/material";
import { TodosProvider } from "../contexts/TodosContext";
import TodoForm from "../sections/todos/TodoForm";
import TodosList from "../sections/todos/TodosList";
import { useParams } from "react-router-dom";
import TodoDialog from "../sections/todos/TodoDialog";

const TodosPage = () => { 
    const { id } = useParams();

    return ((<TodosProvider><Stack spacing={3}><TodosList /><TodoForm /></Stack>{id && <TodoDialog id={id} />}</TodosProvider>))
};

export default TodosPage;