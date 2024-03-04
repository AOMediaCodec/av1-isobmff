import clsx from "clsx";
import { useMemo, useRef, useState } from "preact/hooks";
import { FiDownload } from "react-icons/fi";
import { IoCloseOutline } from "react-icons/io5";
import { useOnClickOutside } from "usehooks-ts";
import coverage_raw from "../../coverage.json";

const BASE_URL = "https://aomediacodec.github.io/av1-isobmff/";
const GIT_REPO =
    "https://github.com/AOMediaCodec/av1-isobmff/raw/main/conformance";

const FilePopover = ({ files }) => {
    const [open, setOpen] = useState(false);
    const ref = useRef(null);
    useOnClickOutside(ref, () => setOpen(false));

    const download = (file) => {
        window.open(`${GIT_REPO}/${file.file_path}`);
    };

    if (files.length === 0) return <span>0</span>;

    return (
        <>
            <button
                className="w-full text-blue-600 hover:text-blue-500 hover:underline"
                onClick={() => setOpen(true)}
            >
                {files.length}
            </button>
            <div
                className={clsx(
                    "fixed left-0 top-0 z-20 h-screen w-screen items-center justify-center bg-black bg-opacity-60 p-8 backdrop-blur-sm backdrop-filter",
                    open ? "flex" : "hidden"
                )}
            >
                <div
                    ref={ref}
                    className="relative flex max-h-[50%] rounded-lg bg-white p-8 max-md:w-full"
                >
                    <div className="absolute -top-2 left-0 flex w-full -translate-y-full flex-row items-center justify-between px-4">
                        <h1 className="text-4xl text-white">
                            {files.length} files found
                        </h1>
                        <IoCloseOutline
                            onClick={() => setOpen(false)}
                            className="cursor-pointer text-6xl text-white"
                        />
                    </div>
                    <div className="scroll flex flex-[1] flex-col items-stretch gap-4 overflow-scroll">
                        {files.map((file) => (
                            <div
                                key={file.file_path}
                                className="flex w-full flex-row items-center justify-between gap-4 border-l-4 border-yellow-400 px-2"
                            >
                                <div className="flex min-w-0 flex-col items-start justify-start">
                                    <span className="w-full min-w-0 truncate text-start text-xl">
                                        {file.file_path
                                            .split("/")
                                            .slice(1)
                                            .join("/")}
                                    </span>
                                    <p className="w-full min-w-0 max-w-lg truncate whitespace-normal text-start text-sm font-light">
                                        {file.description}
                                    </p>
                                </div>
                                <span className="flex h-full w-fit items-center">
                                    <FiDownload
                                        onClick={() => download(file)}
                                        className="cursor-pointer text-2xl duration-100 hover:text-blue-500"
                                    />
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </>
    );
};

const FileTable = ({ children, files }) => {
    return (
        <div className="flex-[33%]">
            <div className="flex w-full flex-col items-center bg-black text-white">
                {children}
            </div>
            <table className="w-full">
                <tbody>
                    {files.sort().map((file) => (
                        <tr>
                            <td className="word-wrap-custom xl:text-sm">
                                <b>{file.split("/")[1]}</b>/
                                {file.split("/").slice(2).join("/")}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

const Table = ({ children, title, color, data, noFileCount, faded }) => {
    if (data.length === 0) return null;
    if (!noFileCount) data.sort((a, b) => b.files.length - a.files.length);

    // Seperate files by their description
    const asserts = {};
    for (const assert of data) {
        if (assert.files.length === 0) {
            asserts[assert.id] = {
                [assert.description]: [],
            };
        }

        for (const file of assert.files) {
            if (!asserts[assert.id]) {
                asserts[assert.id] = {};
            }

            const description = file.description || assert.description;
            if (!asserts[assert.id][description]) {
                asserts[assert.id][description] = [];
            }

            asserts[assert.id][description].push(file);
        }
    }

    // Sort by file count
    for (const assert of Object.keys(asserts)) {
        const values = asserts[assert];
        const sorted = Object.entries(values).sort(
            ([, a], [, b]) => b.length - a.length
        );
        asserts[assert] = Object.fromEntries(sorted);
    }

    const AssertEntry = ({ files, description }) => {
        return (
            <>
                {!noFileCount && (
                    <td className="text-center">
                        <FilePopover files={files} />
                    </td>
                )}
                <td className="word-wrap-custom xl:text-sm">{description}</td>
            </>
        );
    };

    return (
        <div className={clsx("flex-[33%]", faded && "opacity-40")}>
            <div className="flex w-full flex-col items-center bg-black text-white">
                {children}
            </div>
            <table className="w-full">
                <thead>
                    <tr>
                        <th colSpan={noFileCount ? 2 : 3}>
                            <h3 className={clsx(color, "text-xl font-bold")}>
                                {title}
                            </h3>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr className="bg-black text-white">
                        <th>Assert ID</th>
                        {!noFileCount && <th># of files</th>}
                        <th>Description</th>
                    </tr>
                    {Object.keys(asserts).length > 0 &&
                        Object.entries(asserts).map(([id, values]) => {
                            const len = Object.keys(values).length;
                            return (
                                <>
                                    <tr
                                        key={id}
                                        className={clsx(
                                            len == 1 &&
                                                values[Object.keys(values)[0]]
                                                    .length == 0 &&
                                                "bg-yellow-50"
                                        )}
                                    >
                                        <td
                                            className="text-center"
                                            rowSpan={len > 1 ? len + 1 : 1}
                                        >
                                            <a
                                                className="text-blue-600 hover:text-blue-500 hover:underline"
                                                href={`${BASE_URL}#${id}`}
                                            >
                                                {id}
                                            </a>
                                        </td>
                                        {len == 1 && (
                                            <AssertEntry
                                                files={
                                                    values[
                                                        Object.keys(values)[0]
                                                    ]
                                                }
                                                description={
                                                    Object.keys(values)[0]
                                                }
                                            />
                                        )}
                                    </tr>
                                    {len > 1 &&
                                        Object.entries(values).map(
                                            ([description, files]) => (
                                                <tr>
                                                    <AssertEntry
                                                        files={files}
                                                        description={
                                                            description
                                                        }
                                                    />
                                                </tr>
                                            )
                                        )}
                                </>
                            );
                        })}
                </tbody>
            </table>
        </div>
    );
};

export default function App() {
    const coverage = useMemo(() => {
        const files = [];
        const covered = {
            valid: [],
            invalid: [],
            valid_percentage: 0,
            invalid_percentage: 0,
            overall_percentage: 0,
        };
        const not_covered = [];
        const excluded = [];

        for (const assert of coverage_raw["rules"]) {
            // Exclude asserts
            if (assert.exclude) {
                excluded.push({
                    id: assert.id,
                    description: assert.description,
                    files: [],
                });
                continue;
            }

            // Filter files and add for valid
            covered.valid.push({
                id: assert.id,
                description: assert.description,
                files: assert.successful_checks.filter((file) => !file.invalid),
            });
            files.push(
                ...assert.successful_checks.map((file) => file.file_path)
            );

            // Filter files and add for invalid
            const invalid_files = assert.warnings.concat(assert.errors);
            covered.invalid.push({
                id: assert.id,
                description: assert.description,
                files: invalid_files.filter((file) => file.invalid),
            });
            files.push(...invalid_files.map((file) => file.file_path));

            // Add to not covered
            if (
                assert.successful_checks.length === 0 &&
                assert.warnings.length === 0 &&
                assert.errors.length === 0
            ) {
                not_covered.push({
                    id: assert.id,
                    description: assert.description,
                    files: [],
                });
            }
        }

        covered.valid_percentage =
            covered.valid.filter((a) => a.files.length != 0).length /
            (coverage_raw["rules"].length - excluded.length);
        covered.invalid_percentage =
            covered.invalid.filter((a) => a.files.length != 0).length /
            (coverage_raw["rules"].length - excluded.length);
        covered.overall_percentage =
            (covered.valid_percentage + covered.invalid_percentage) / 2;

        return {
            files: [...new Set(files)],
            covered,
            not_covered,
            excluded,
        };
    }, []);

    return (
        <div className="container mx-auto flex w-full flex-col gap-6 p-8">
            <div className="flex flex-row flex-wrap justify-between gap-4">
                <div className="flex flex-col gap-4">
                    <h1 className="text-4xl font-thin tracking-tight">
                        AV1 Codec ISO Media File Format Binding Specification Coverage Report
                    </h1>
                    <span>
                        <a
                            className="text-blue-500 underline"
                            href="https://github.com/gpac/ComplianceWarden"
                        >
                            Compliance Warden
                        </a>{" "}
                        version: {coverage_raw["cw_version"]}
                    </span>
                    <span className="border-l-4 border-red-400 pl-2 text-xl">
                        <b>WARNING: </b> These files are still{" "}
                        <u>under review.</u>
                    </span>
                </div>
            </div>
            <div className="flex flex-col flex-wrap items-stretch justify-center gap-6 xl:flex-row">
                <Table
                    title={
                        <>
                            Valid Files <i>(with warnings)</i>
                        </>
                    }
                    color="bg-green-400"
                    data={coverage.covered.valid}
                >
                    <span className="text-center text-2xl font-bold">
                        Coverage:{" "}
                        {(coverage.covered.valid_percentage * 100).toFixed(2)}%
                    </span>
                    <p>Files that sucessfully execute the rule</p>
                </Table>
                <Table
                    title="Invalid Files"
                    color="bg-red-400"
                    data={coverage.covered.invalid}
                >
                    <span className="text-center text-2xl font-bold">
                        Coverage:{" "}
                        {(coverage.covered.invalid_percentage * 100).toFixed(2)}
                        %
                    </span>
                    <p>
                        Files that <u>do not</u> sucessfully execute the rule
                    </p>
                </Table>
                <FileTable files={coverage.files}>
                    Files used to create the coverage
                </FileTable>
                <Table
                    title="Excluded from Coverage"
                    color="bg-neutral-400"
                    data={coverage.excluded}
                    noFileCount
                    faded
                />
            </div>
        </div>
    );
}
