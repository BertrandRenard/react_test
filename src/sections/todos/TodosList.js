import React, { useEffect } from 'react'
import useTodos from '../../hooks/useTodos';
import TodoCard from './TodoCard';
import { Divider, Stack } from '@mui/material';

const TodosList = () => {
  const [{ todos, fetching }, { getTodos }] = useTodos();
  
  useEffect(() => {
    getTodos();
  }, []);
  
  return (
    <>{fetching && 'Fetching Todos...'}
      <Stack spacing={2} divider={<Divider />}>
        {todos.map((todo) => <TodoCard todo={todo} />)}
      </Stack>
    </>

  )
}

export default TodosList