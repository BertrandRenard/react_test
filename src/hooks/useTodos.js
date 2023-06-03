import { useContext } from "react";
import { TodosContext } from "../contexts";

const useTodos = () => useContext(TodosContext);

export default useTodos;