import Link from "next/link";
import { History } from "./history";

export const Navbar = async () => {
  let session = { user: { email: 'local@example.com' } };

  return (
    <div className="bg-white absolute top-0 left-0 w-dvw border-b dark:border-zinc-800 py-2 px-3 justify-between flex flex-row items-center dark:bg-zinc-900 z-30">
      <div className="flex flex-row gap-3 items-center">
        <History />
        <div className="text-sm dark:text-zinc-300">
          Internal Knowledge Base
        </div>
      </div>

      <div className="group py-1 px-2 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 cursor-pointer relative">
        <div className="text-sm dark:text-zinc-400 z-10">
          {session.user?.email}
        </div>
      </div>
    </div>
  );
};
