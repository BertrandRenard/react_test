import { Button, Stack, TextField } from '@mui/material'
import React, { useState } from 'react'
import useTodos from '../../hooks/useTodos'

const TodoForm = () => {
    const [task, setTask] = useState('');
    const [_, { createTodo }] = useTodos();
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        await createTodo({ task });
        setTask('')
    };
    
  return (
    <Stack onSubmit={handleSubmit} component='form' spacing={2}>
        <TextField value={task} onChange={(e) => setTask(e.target.value)} required placeholder="Describe your task" />
        <Button type='submit' variant='outlined'>Ajouter</Button>
    </Stack>
  )
}

export default TodoForm