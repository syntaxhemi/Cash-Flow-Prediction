import { TbBrandCashapp } from "react-icons/tb";

const Navbar = () => {
    return (
        <div className="flex w-full px-50 py-6 bg-white">
            <div className="flex items-center gap-2">
                <TbBrandCashapp className="text-3xl text-blue-700" />
                <h3 className="text-2xl">
                    <strong>Cash Flow</strong>
                </h3>
            </div>
        </div>
    );
};

export default Navbar;
