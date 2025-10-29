const Input = ({ data, setData, name, label }) => {
    const handleChange = (e) => {
        setData((prev) => ({
            ...prev,
            [name]: e.target.value,
        }));
    };

    return (
        <div className="flex flex-col gap-1 w-full">
            <label htmlFor={name} className="text-blue-900">
                {label}
            </label>
            <input
                id={name}
                name={name}
                type="number"
                value={data[name]}
                onChange={handleChange}
                className="w-full px-3 py-1 rounded-sm focus:outline-none focus:border border-blue-200 text-blue-900 bg-white [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
            />
        </div>
    );
};

export default Input;
