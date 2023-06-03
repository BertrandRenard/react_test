import axios from "axios";
import { useReducer, useState } from "react";
import { createContext } from "react";
import PATHS from "../routes/path";
import { useNavigate } from "react-router-dom";

const API_URL = 'http://localhost:8000';

const initialState = { todos: [], selectedTodo: null };

const TodosContext = createContext(initialState);

const reducer = (state, action) => {
    if (action.type === 'GET_TODOS') return { ...state, todos: action.payload  };
    if (action.type === 'GET_TODO') return { ...state, selectedTodo: action.payload  };
    if (action.type === 'CREATE_TODO') return { ...state, todos: [...state.todos, action.payload]  };
    if (action.type === 'UPDATE_TODO') return { ...state, todos: state.todos.map((todo) => todo.id === action.payload.id ? action.payload : todo)  };
    if (action.type === 'DELETE_TODO') return { ...state, todos: state.todos.filter((todo) => todo.id !== action.payload)  };

    return state;
};
    
const TodosProvider = ({ children }) => {
    const navigate = useNavigate();
    
    const [state, dispatch] = useReducer(reducer, initialState);
    const [fetching, setFetching] = useState(false);

    const getTodos = async () => {
        setFetching(true);
        const { data } = await axios.get(`${API_URL}/todos`);
        dispatch({ type: 'GET_TODOS', payload: data });
        setFetching(false);
    }

    const getTodo = async (id) => {
        try {
        const { data } = await axios.get(`${API_URL}/todos/${id}`);
        dispatch({ type: 'GET_TODO', payload: data });
        }catch {
            navigate(`${PATHS.todo.list}`, { replace: true });
        }
    }

    const createTodo = async (todo) => {
        const { data } = await axios.post(`${API_URL}/todos`, todo);
        dispatch({ type: 'CREATE_TODO', payload: data });
    };

    const updateTodo = async (todoId, todo) => {
        const { data } = await axios.put(`${API_URL}/todos/${todoId}`, todo);
        dispatch({ type: 'UPDATE_TODO', payload: data });
    };

    const deleteTodo = async (todoId) => {
        await axios.delete(`${API_URL}/todos/${todoId}`);
        dispatch({ type: 'DELETE_TODO', payload: todoId });
    };

    const methods = { getTodos, createTodo, deleteTodo, getTodo, updateTodo };
    
    return <TodosContext.Provider value={[{ ...state, fetching }, methods]}>{children}</TodosContext.Provider>;
}
    
export { TodosProvider };
export default TodosContext;