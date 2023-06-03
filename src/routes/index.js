import MainLayout from '../layouts/MainLayout';
import { TodosPage } from '../pages';
import { Navigate, useRoutes } from "react-router-dom";

const todosRoutes = [
    {
        index: true,
        element: <Navigate replace to='/todos' />,
    },
    {
        path: 'todos',
        element: <MainLayout />,
        children: [
            { index: true, element: <TodosPage /> },
        ],
    },
    {
        path: '*',
        element: <Navigate replace to='' />,
    },
];
    
const Router = ({ children }) => {
    return useRoutes([...todosRoutes]);
};
    
export default Router;