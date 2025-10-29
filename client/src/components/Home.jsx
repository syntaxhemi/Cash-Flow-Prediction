import Navbar from "./Navbar";
import Prediction from "./Prediction";

const Home = () => {
    return (
        <div className="flex flex-col">
            <Navbar />
            <Prediction />
        </div>
    );
};

export default Home;
