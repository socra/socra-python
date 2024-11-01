import React, { useState, useEffect, useRef } from 'react';

const CoolComponent: React.FC = () => {
    const [count, setCount] = useState(0);
    const [message, setMessage] = useState('Hello, World!');
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        console.log('Component mounted or count changed:', count);
    }, [count]);

    const focusInput = () => {
        if (inputRef.current) {
            inputRef.current.focus();
        }
    };

    return (
        <div>
            <h1>{message}</h1>
            <button onClick={() => setCount(count + 1)}>Increment Count</button>
            <p>Current Count: {count}</p>
            <input ref={inputRef} type="text" placeholder="Type something..." />
            <button onClick={focusInput}>Focus Input</button>
        </div>
    );
};

export default CoolComponent;